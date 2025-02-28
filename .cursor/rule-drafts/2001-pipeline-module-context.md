---
description: PROVIDE cross-component context when EDITING pipeline-related files to ENSURE consistent implementation
globs: backend/workers/tasks/*.py, backend/services/*_service.py, backend/database/models/pipeline_*.py, frontend/src/pages/Pipeline*.tsx, frontend/src/components/automation/Pipeline*.tsx, frontend/src/components/pipelines/**/*.tsx
alwaysApply: false
---

# Pipeline Module Cross-Component Context

<version>1.4.0</version>

## Context
- When editing any pipeline-related files in either backend or frontend
- When implementing new pipeline features that span both backend and frontend
- When debugging pipeline functionality issues
- When modifying pipeline execution logic or flow
- When working with type annotations in pipeline/celery task code

## Pipeline/Task Architecture and Execution Flow

### Core Concepts
- **Templates vs Runs**: Templates define reusable structure and configuration, while Runs are execution instances
- **Pipeline Template**: Defines the structure of a workflow with connected tasks
- **Pipeline Run**: A specific execution instance of a pipeline template
- **Task Template**: Defines the operation a task performs (Docker command, parameters, etc.)
- **Task Run**: A specific execution instance of a task template within a pipeline run

### Type Handling in Pipeline Code
- **Beanie Models Type Requirements**:
  - When working with `init_beanie()`, use `# type: ignore` comments to suppress mypy errors with document_models
  - Models list must be properly initialized as document types compatible with Beanie
  - For MongoDB async operations, use proper type annotations for AsyncIOMotorClient and AsyncIOMotorDatabase

- **Celery Task Type Handling**:
  - Celery tasks need proper type annotations to ensure type safety
  - Use `# type: ignore[no-any-unimported]` for celery task decorators to handle circular imports
  - For functions decorated with `@typed_celery_task`, ensure proper typing for all parameters 
  - When using CeleryTask objects, properly type all their attributes

- **Async/Sync Type Bridging**:
  - Functions that bridge async/sync boundaries (like celery tasks) need explicit annotations
  - When running async code from sync contexts with `asyncio.run()`, explicitly type the return values
  - Use proper error handling with typed Exception objects

### Data Flow and Relationships
- Pipeline Templates contain multiple Task Templates via `task_template_ids`
- Flow Connections (`flow_connections`) define the directed graph between tasks:
  - `from_id`: Source task node ID
  - `to_id`: Target task node ID
  - `on_state`: Required state of source task to trigger target (default: "success")
- Task Positions (`task_positions`) define UI placement and task-specific parameters
- Each Pipeline Run creates Task Runs for all tasks in the template

### Pipeline Execution Model
1. **Pipeline Initiation**
   - Created via API request (manual) or scheduler (scheduled/recurring)
   - Trigger types: `MANUAL`, `SCHEDULED`, `RECURRING`
   - Pipeline types: `SINGLE_AUTOMATION`, `MULTI_AUTOMATION`

2. **Task Creation**
   - Task runs are created for each task template in the pipeline
   - Each gets a unique node ID and inherits template parameters
   - Parameters can be overridden at the pipeline level

3. **Queue Management**
   - Only one pipeline per automation type runs at a time
   - Pipelines of the same automation type wait in a queue
   - Each pending pipeline has a `queue_position` indicating its place in line
   - Pipeline runs with state `RUNNING` have a queue position of 0
   - Pipeline runs with state `PENDING` have queue positions starting from 1, ordered by creation time
   - Queue positions are updated whenever:
     - A new pipeline run is created
     - A pipeline run's state changes
     - The `check_pending_pipelines` task runs
   - The UI displays the queue position to inform users of wait time

4. **Execution Flow**
   - **Task State Progression**: PENDING → QUEUED → RUNNING → [SUCCESS|FAILURE|ERROR|CANCELLED]
   - **Initial Tasks**: Tasks with no incoming connections execute first
   - **Subsequent Tasks**: Execute when all parent tasks reach required states (based on flow connections)
   - **Pipeline State**: Derived from constituent task states
   - **Conditional Execution**: Tasks can be configured to run based on specific states of parent tasks:
     - Default flow is on parent "success" state
     - Tasks can also be configured to run on parent "failure" or "error" states
     - This enables error-handling and alternative execution paths

5. **Pipeline State Management**
   - Pipeline remains in RUNNING state as long as any tasks are active (PENDING, QUEUED, RUNNING)
   - Pipeline transitions to FAILURE if any task fails AND no more tasks can be executed
   - Pipeline transitions to SUCCESS only when all tasks complete successfully
   - Pipeline transitions to CANCELLED if all tasks are cancelled
   - A pipeline with failed tasks may still complete successfully if all required paths execute

6. **Task Execution**
   - Tasks run in Docker containers with specified commands
   - Environment is prepared with git repo cloning, requirements installation
   - Exit code determines task success/failure
   - All logs (including errors) are captured and stored in the task run logs collection

7. **Flow Coordination**
   - Once a task completes, system checks for successor tasks via flow connections
   - Tasks only execute when their parent tasks reach the required states specified in flow_connections
   - If a task fails, dependent tasks are only cancelled if they can no longer satisfy their conditions
   - The system preserves tasks that depend on failure states of other tasks
   - Pipeline is marked complete when all tasks reach terminal states or no more tasks can be executed

8. **Stale Pipeline Cleanup**
   - A scheduled task runs periodically to detect and clean up stale pipelines
   - Pipelines in the RUNNING state for longer than `MAX_PIPELINE_RUN_HOURS` (default: 24) are considered stale
   - Stale pipelines are automatically moved to the CANCELLED state
   - Associated task runs are also cancelled and the reason is logged
   - This prevents indefinitely running pipelines from blocking the queue
   - The cleanup task runs every 30 minutes via Celery beat

### Automation Types
- Tasks and pipelines have specific automation types that determine execution context
- Automation types (e.g., `EP_360_FE`, `APPLICATION_BE`) define which execution queue to use
- Pipeline inherits automation types from constituent tasks
- Each automation type has a dedicated queue and only runs one pipeline at a time

### Log Streaming and Visualization
- **WebSocket Log Streaming**: Task logs are streamed in real-time to the frontend via WebSockets
- **Connection Management**: WebSocket connections are managed by the `ConnectionManager` in `backend/ws/manager.py`
- **Subscription Model**:
  - Clients subscribe to specific task runs via WebSocket
  - Authentication is handled via token in initial connection message
  - Both real-time streaming and historical log retrieval are supported
- **Log Storage**:
  - Logs are captured during task execution and stored in the TaskRun model
  - Each log entry includes timestamp, message, and log level (info, error, etc.)
  - Error information is stored as log entries with `type: "error"` (not in a separate field)
  - Logs persist after task completion for later analysis

### Pipeline Detail Modal
- **Modal Interface**: Pipeline runs can be visualized via the PipelineRunDetailsModal component
- **Dual View**:
  - Task List View: Shows all tasks with status indicators and live terminal
  - Flow Map View: Visualizes the directed graph of pipeline tasks and their connections
- **Terminal View**:
  - Real-time log streaming for active tasks via WebSockets
  - Automatic reconnection if WebSocket connections fail
  - Color-coded log levels for better readability
  - Automatic scrolling to show latest logs
  - Error messages highlighted from logs with `type: "error"`
- **Queue Status Display**:
  - Shows current queue position for pending pipeline runs
  - Indicates when a pipeline is actively running (position 0)
  - Updates in real-time as pipeline states change
- **Task Selection**: Users can select tasks to view specific logs
- **Status Monitoring**: Pipeline and task states are updated in real-time

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend pipeline behavior
- When modifying execution flow, test all affected pipeline state transitions
- Update both template and run components when adding new fields or properties
- Use proper type annotations when working with pipeline code:
  - Explicitly type all function parameters and return values
  - Use proper type hints for MongoDB/Beanie models
  - Add type ignore comments with specific error codes when necessary
  - Properly construct schema class instances instead of using dictionaries
- When creating instances from Pydantic models, always use the model constructor instead of passing dictionaries
- When handling task errors in pipelines:
  - Store error information in logs with `type: "error"` and appropriate timestamps
  - Set the task state to indicate the error condition (ERROR, FAILURE)
  - Evaluate downstream tasks based on the error state per flow connection rules
- When modifying queue management:
  - Update queue positions whenever pipeline state changes
  - Ensure only one pipeline runs per automation type
  - Maintain the FIFO order of the pipeline queue
  - Update the UI to reflect current queue position
- When working with stale pipeline cleanup:
  - Use the `MAX_PIPELINE_RUN_HOURS` setting from config
  - Properly cancel both the pipeline run and all associated task runs
  - Add detailed logs explaining why the pipeline was cancelled
  - Consider effects on downstream systems that might depend on pipeline completion

## Related Files

[pipeline_templates.py](mdc:backend/api/v1/endpoints/pipeline_templates.py)

[pipeline_runs.py](mdc:backend/api/v1/endpoints/pipeline_runs.py)

[pipeline_template.py](mdc:backend/schemas/pipeline_template.py)

[pipeline_run.py](mdc:backend/schemas/pipeline_run.py)

[pipeline_template_service.py](mdc:backend/services/pipeline_template_service.py)

[pipeline_run_service.py](mdc:backend/services/pipeline_run_service.py)

[pipeline_executor.py](mdc:backend/workers/tasks/pipeline_executor.py)

[executor.py](mdc:backend/workers/tasks/executor.py)

[celery_app.py](mdc:backend/workers/celery_app.py)

[config.py](mdc:backend/core/config.py)

[manager.py](mdc:backend/ws/manager.py)

[PipelineBuilder.tsx](mdc:frontend/src/pages/PipelineBuilder.tsx)

[PipelineRunDetailsModal.tsx](mdc:frontend/src/components/automation/PipelineRunDetailsModal/PipelineRunDetailsModal.tsx)

[PipelineTemplateBuilderPage.module.css](mdc:frontend/src/pages/PipelineTemplateBuilderPage.module.css)

[PipelineTemplateBuilder.tsx](mdc:frontend/src/components/pipelines/PipelineTemplateBuilder/PipelineTemplateBuilder.tsx)

[PipelineTemplateBuilderModal.tsx](mdc:frontend/src/components/pipelines/PipelineTemplateBuilderModal/PipelineTemplateBuilderModal.tsx)

[PipelineTemplateSmartEdge.tsx](mdc:frontend/src/components/pipelines/SmartEdge/PipelineTemplateSmartEdge.tsx)

[PipelineTemplateTaskNode.tsx](mdc:frontend/src/components/pipelines/TaskNode/PipelineTemplateTaskNode.tsx)

## Examples
<example>
When adding support for conditional task execution:
1. Update the FlowConnection model in pipeline_template.py to include condition field
2. Modify pipeline_executor.py to evaluate conditions before queueing successor tasks
3. Update the pipeline_template_service.py to validate condition expressions
4. Run the API generation script to update frontend types
5. Extend PipelineBuilder.tsx to allow setting conditions on connections
6. Add UI components to visualize conditional paths in the pipeline graph
</example>

<example>
When working with Celery tasks in pipeline code:
1. Use proper type annotations for celery tasks:
   ```python
   @typed_celery_task(name="pipeline.execute", bind=True)
   def execute_pipeline(self: CeleryTask, pipeline_id: str) -> bool:  # type: ignore[no-any-unimported]
       """Celery entrypoint to execute a pipeline."""
       try:
           # Get task_id from request
           task_id = self.request.id if self.request else None
           # Add explicit type annotation to help mypy
           result: bool = asyncio.run(_execute_pipeline(ObjectId(pipeline_id), task_id))
           return result
       except Exception as e:
           logger.error(f"Error executing pipeline {pipeline_id}: {str(e)}")
           return False
   ```
2. When calling init_beanie with models:
   ```python
   # Type ignore for mypy since it doesn't understand beanie's init_beanie correctly
   await init_beanie(database=db, document_models=models)  # type: ignore
   ```
3. Use proper schema class initialization:
   ```python
   # Correct:
   run_data = PipelineRunCreate(
       pipeline_template_id=str(template.id),
       automation_types=template.automation_types,
       task_template_ids=template.task_template_ids,
       flow_connections=template.flow_connections,
       task_positions=template.task_positions
   )
   
   # Incorrect:
   run_data = {
       "pipeline_template_id": str(template.id),
       "automation_types": template.automation_types,
       "task_template_ids": template.task_template_ids,
       # Missing fields that are required
   }
   ```
</example>

<example>
When implementing queue position management:
```python
async def update_queue_positions(self, automation_type: str) -> None:
    """
    Update queue positions for all pending pipeline runs of the same automation type.
    Pipeline runs in the RUNNING state have position 0.
    Pipeline runs in the PENDING state are ordered by created_at time.
    """
    logger.info(f"Updating queue positions for automation type: {automation_type}")
    
    # Find all non-terminal pipeline runs of this automation type, ordered by created_at
    pipeline_runs = await PipelineRun.find(
        {
            "automation_types": automation_type,
            "state": {"$in": [PipelineState.PENDING.value, PipelineState.RUNNING.value]}
        }
    ).sort("created_at").to_list()
    
    position = 0
    for run in pipeline_runs:
        # Running pipeline runs have position 0, pending ones start at position 1
        new_position = 0 if run.state == PipelineState.RUNNING.value else position + 1
        
        # Only update if the position has changed
        if run.queue_position != new_position:
            run.queue_position = new_position
            await run.save()
            
        # Only increment position for RUNNING pipelines
        if run.state == PipelineState.RUNNING.value:
            position += 1
```
</example>

<example>
When implementing cleanup for stale pipelines:
```python
async def cleanup_stale_pipelines_async() -> bool:
    """Find and cancel pipeline runs that have been in the running state for too long."""
    try:
        await init_db()
        
        # Define what "too long" means - default to 24 hours
        max_run_time = timedelta(hours=settings.MAX_PIPELINE_RUN_HOURS 
                               if hasattr(settings, 'MAX_PIPELINE_RUN_HOURS') else 24)
        
        cutoff_time = get_israel_time() - max_run_time
        
        # Find all pipelines in the RUNNING state that started before the cutoff time
        stale_pipelines = await PipelineRun.find({
            "state": PipelineState.RUNNING.value, 
            "started_at": {"$lt": cutoff_time}
        }).to_list()
        
        # Cancel each stale pipeline run
        for pipeline_run in stale_pipelines:
            # Set the pipeline state to CANCELLED
            pipeline_run.state = PipelineState.CANCELLED
            pipeline_run.completed_at = get_israel_time()
            
            # Add a note to the pipeline run
            cancel_reason = f"Automatically cancelled after running for more than {max_run_time.total_seconds() / 3600} hours"
            await pipeline_run.save()
            
            # Cancel any task runs that are still running
            for task_id in pipeline_run.task_run_ids:
                task_run = await TaskRun.get(ObjectId(task_id))
                if task_run and task_run.state in [TaskState.PENDING, TaskState.QUEUED, TaskState.RUNNING]:
                    task_run.state = TaskState.CANCELLED
                    task_run.completed_at = get_israel_time()
                    task_run.logs.append({
                        "type": "error",
                        "timestamp": format_israel_time(get_israel_time()),
                        "message": cancel_reason,
                    })
                    await task_run.save()
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning up stale pipelines: {str(e)}")
        return False
```
</example>

<example type="invalid">
Adding a new pipeline execution mode without:
1. Updating both template and run models
2. Modifying the execution flow in pipeline_executor.py
3. Adding validation in the pipeline service
4. Updating the frontend components to support the new mode

This would result in inconsistent behavior between UI expectations and actual execution.
</example>

<example type="invalid">
Incorrect error handling in pipeline tasks:
```python
# Missing error logging
async def execute_task_async(task_id: str) -> bool:
    try:
        # Task execution code...
        return True
    except Exception as e:
        # Only setting state without adding to logs
        task_run.state = TaskState.ERROR
        # Error information is lost - should add to logs
        # Missing: task_run.logs.append({"type": "error", "timestamp": timestamp, "message": str(e)})
        await task_run.save()
        return False
```
</example>

<example type="invalid">
Incorrect queue position management:
```python
# This implementation doesn't consider automation type isolation
async def check_pending_pipelines_async() -> None:
    pipeline_runs = await PipelineRun.find({"state": PipelineState.PENDING.value}).to_list()
    for pipeline_run in pipeline_runs:
        # Incorrect: Doesn't check if another pipeline of same automation type is running
        pipeline_run.state = PipelineState.RUNNING
        await pipeline_run.save()
        await queue_initial_tasks(pipeline_run)
```
</example>
