---
description: PROVIDE cross-component context when EDITING task-related files to ENSURE consistent implementation
globs: backend/api/v1/endpoints/task_*.py, backend/schemas/task_*.py, frontend/src/pages/AutomationTypePage*, backend/services/task_*.py, backend/workers/runners/*, backend/workers/tasks/executor.py, backend/ws/manager.py, frontend/src/components/automation/PipelineRunDetailsModal/*, frontend/src/components/tasks/**/*.tsx
alwaysApply: false
---

# Task Module Cross-Component Context

<version>1.3.0</version>

## Context
- When editing any task-related files in either backend or frontend
- When implementing new task features that span both backend and frontend
- When debugging task functionality issues
- When modifying task execution logic or parameters
- When working with type annotations in task execution code

## Task Architecture and Execution Flow

### Core Concepts
- **Task Template**: Defines what a task does, including:
  - Task type (Docker, Shell, Python)
  - Task category (Docker, Shell, Python, Automation, Service, Custom)
  - Automation type (EP_360_FE, APPLICATION_BE, etc.)
  - Parameters and required parameters
  - Command to execute
- **Task Run**: Instance of a task template execution, including:
  - Reference to task template
  - Optional reference to pipeline run (if part of pipeline)
  - Node ID (unique identifier within pipeline graph)
  - Execution state and logs
  - Parameters (can override template parameters)
  - Input/output data

### Type Handling in Task Code
- **Beanie Models Type Requirements**:
  - When working with `init_beanie()`, use `# type: ignore` comments for document_models
  - Use proper type annotations for AsyncIOMotorClient and AsyncIOMotorDatabase
  - Follow invariant vs covariant type guidelines for collections

- **Celery Task Type Handling**:
  - Use `# type: ignore[no-any-unimported]` with celery task decorators to handle circular imports
  - For functions decorated with `@typed_celery_task`, ensure proper parameter and return type annotations
  - When using CeleryTask objects, properly handle request attributes that might be None

- **Docker Execution Type Safety**:
  - Properly type all container configuration parameters
  - Use explicit typing for command outputs and log handling
  - Handle string conversions and encoding/decoding with appropriate error handling

### Task Types and Categories
- **Docker Tasks**: Run in isolated containers with configurable environments
- **Shell Tasks**: Execute shell commands directly
- **Python Tasks**: Execute Python code directly
- **Automation Tasks**: Specialized tasks for automation purposes
- **Service Tasks**: Long-running service operations
- **Custom Tasks**: Custom implementation for special purposes

### Task Execution Model
1. **Task Initialization**
   - Created directly or as part of a pipeline run
   - Initial state: PENDING
   - Parameters inherited from template, can be overridden

2. **Execution Preparation**
   - Task state transitions to QUEUED when ready to execute
   - If part of pipeline, waits for parent tasks to reach required states
   - Gets assigned to a worker based on automation type

3. **Task Execution Flow**
   - Docker container is created with Python base image
   - Environment is prepared (dependencies, git repos, env files)
   - Command is executed with required parameters
   - Logs and exit codes are captured
   - State transitions based on execution result:
     - Exit code 0 → SUCCESS
     - Non-zero exit code → FAILURE
     - Exception during execution → ERROR
     - Manual cancellation → CANCELLED

4. **Task States**
   - PENDING: Initial state, not yet queued
   - QUEUED: Ready to execute, waiting for worker
   - RUNNING: Currently executing
   - SUCCESS: Successfully completed
   - FAILURE: Failed during execution (non-zero exit code)
   - ERROR: Error occurred before/during execution
   - CANCELLED: Manually cancelled or cancelled due to dependency failure
   - SKIPPED: Not executed due to pipeline conditions

5. **Parameter Handling**
   - Templates define required and optional parameters
   - Parameters can be overridden at task run creation
   - Position-specific parameters from pipeline can override defaults
   - Special handling for common parameters:
     - `command`: The command to execute
     - `repo_url`: Git repository to clone
     - `env_content`: Environment variables
     - `requirements_content`: Python dependencies

6. **Log Handling and Streaming**
   - **Log Capture and Storage**:
     - Logs are captured during container execution
     - Each log entry contains timestamp, log level, and message
     - All logs (including errors) are stored in the TaskRun model's `logs` array
     - Error information is stored as log entries with `type: "error"`
     - Logs persist after task completion for historical analysis
   - **WebSocket Streaming**:
     - Real-time log streaming uses WebSockets via `ConnectionManager`
     - Clients connect to `/api/v1/tasks/runs/{task_id}/logs/ws` endpoint
     - Authentication via token in initial connection message
     - Subscription-based model for targeted task log delivery
   - **Terminal Visualization**:
     - Logs are displayed in an interactive terminal UI
     - Color-coded based on log level (info, error, warning, etc.)
     - Support for real-time streaming and historical log viewing
     - Auto-scrolling to follow new log entries in real time
   - **Error Handling**:
     - All error messages are stored as log entries with `type: "error"`
     - Standard error log structure: `{ type: "error", timestamp: "ISO-formatted date", message: "Error description" }`
     - Frontend can filter logs to show only errors or all logs
     - UI can display error indicators based on presence of error logs

### Integration with Pipeline System
- Tasks can exist independently or as part of pipelines
- In pipelines, tasks are connected via flow connections
- Tasks can have position information for visual representation
- Task state changes trigger evaluation of successor tasks in pipeline

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend task behavior
- When adding new task types or parameters, update executor logic
- Test all task state transitions when modifying execution flow
- Use proper type annotations when working with task code:
  - Explicitly type all function parameters and return values
  - Use proper type hints for MongoDB/Beanie models
  - Add type ignore comments with specific error codes when necessary
  - Properly construct schema class instances instead of using dictionaries
- When accessing attributes that might be None, perform proper null checks:
  - Use conditional expressions like `value = obj.attr if obj and hasattr(obj, "attr") else None`
  - Use type narrowing with is-checks, especially with CeleryTask requests
- When handling errors, always add them to the logs collection with proper structure:
  - Use consistent log entry structure with type, timestamp, and message
  - Set task state appropriately (ERROR, FAILURE) to reflect issue
  - Avoid relying on external error fields or properties

## Related Files

[task_templates.py](mdc:backend/api/v1/endpoints/task_templates.py)

[task_runs.py](mdc:backend/api/v1/endpoints/task_runs.py)

[task_template.py](mdc:backend/schemas/task_template.py)

[task_run.py](mdc:backend/schemas/task_run.py)

[task_template_service.py](mdc:backend/services/task_template_service.py)

[task_run_service.py](mdc:backend/services/task_run_service.py)

[executor.py](mdc:backend/workers/tasks/executor.py)

[celery_app.py](mdc:backend/workers/celery_app.py)

[base_runner.py](mdc:backend/workers/runners/base_runner.py)

[docker_runner.py](mdc:backend/workers/runners/docker_runner.py)

[task_runner.py](mdc:backend/workers/runners/task_runner.py)

[manager.py](mdc:backend/ws/manager.py)

[AutomationTypePage.tsx](mdc:frontend/src/pages/AutomationTypePage.tsx)

[PipelineRunDetailsModal.tsx](mdc:frontend/src/components/automation/PipelineRunDetailsModal/PipelineRunDetailsModal.tsx)

[AutomationTypePage.module.css](mdc:frontend/src/pages/AutomationTypePage.module.css)

[TaskForm.tsx](mdc:frontend/src/components/tasks/TaskForm/TaskForm.tsx)

[TaskDetails.module.css](mdc:frontend/src/components/tasks/TaskDetails/TaskDetails.module.css)

[TaskDetailsHeader.module.css](mdc:frontend/src/components/tasks/TaskDetailsHeader/TaskDetailsHeader.module.css)

[TaskDetailsTerminal.module.css](mdc:frontend/src/components/tasks/TaskDetailsTerminal/TaskDetailsTerminal.module.css)

[TasksTable.module.css](mdc:frontend/src/components/tasks/TasksTable/TasksTable.module.css)

## Examples
<example>
When adding a new task parameter for custom environment variables:
1. Update the TaskTemplate schema in task_template.py to include the environment_variables field
2. Modify executor.py to inject these variables into the Docker container
3. Update the task_template_service.py to validate environment variable names and values
4. Run the API generation script to update frontend types
5. Extend AutomationTypePage.tsx to allow setting environment variables
6. Add UI form components for environment variable key-value pairs
7. Add validation for variable names following environment variable conventions
</example>

<example>
Proper error handling in task execution code:
```python
async def execute_task_async(task_id: str) -> bool:
    """Execute a task asynchronously (within an async event loop)."""
    task_run: Optional[TaskRun] = None
    try:
        await init_db()
        task_run = await TaskRun.get(ObjectId(task_id))
        if not task_run:
            logger.error(f"Task run {task_id} not found")
            return False
            
        # Task execution logic here
        
        return True
    except Exception as e:
        # Proper error handling with logging
        error_msg = f"Error executing task: {str(e)}"
        logger.error(error_msg)
        if task_run:
            task_run.state = TaskState.ERROR
            # Add error message to logs with proper structure
            task_run.logs.append({
                "type": "error",
                "timestamp": format_israel_time(get_israel_time()),
                "message": error_msg,
            })
            await task_run.save()
        return False
```
</example>

<example>
When implementing enhanced log streaming capabilities:
1. Modify the ConnectionManager in manager.py to support log filtering by severity
2. Update the task_run.py schema to include structured log metadata
3. Enhance the executor.py log capture to include source and context information
4. Create a new WebSocket endpoint for filtered log streaming
5. Update PipelineRunDetailsModal.tsx to include log filtering controls
6. Add color-coding and formatting to the terminal display based on log metadata
7. Implement client-side caching to improve performance with large log volumes
</example>

<example type="invalid">
Adding a new task type without:
1. Updating the TaskType enum in types.py
2. Implementing the execution logic in executor.py
3. Adding validation in the task service
4. Updating the frontend to support creating and configuring the new task type

This would result in tasks that can be created but not properly executed or displayed.
</example>

<example type="invalid">
Poor error handling in task code:
```python
# Missing type annotations and incorrect error handling
def execute_task(self, task_id):  # Missing return type and parameter typing
    asyncio.run(execute_task_async(task_id))  # No error handling or return value
    
async def execute_task_async(task_id):  # Missing return type
    task_run = await TaskRun.get(ObjectId(task_id))
    
    try:
        # Task execution code
        pass
    except Exception as e:
        # Incorrect error handling - not using structured logs
        task_run.state = TaskState.ERROR
        # Missing proper error logging in the logs collection
        # Should use: task_run.logs.append({"type": "error", "timestamp": timestamp, "message": str(e)})
        await task_run.save()
```
</example>
