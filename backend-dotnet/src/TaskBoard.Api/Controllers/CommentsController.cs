using Microsoft.AspNetCore.Mvc;
using TaskBoard.Api.Models;
using TaskBoard.Api.Services;

namespace TaskBoard.Api.Controllers;

[ApiController]
[Route("api/tasks/{taskId:int}/comments")]
public class CommentsController : ControllerBase
{
    private readonly ICommentService _service;

    public CommentsController(ICommentService service) => _service = service;

    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<CommentResponse>>> List(int taskId, CancellationToken ct)
    {
        try { return Ok(await _service.ListAsync(taskId, ct)); }
        catch (TaskNotFoundException ex) { return NotFound(new { error = ex.Message }); }
    }

    [HttpGet("count")]
    public async Task<ActionResult<CommentCountResponse>> Count(int taskId, CancellationToken ct)
    {
        try { return Ok(new CommentCountResponse(await _service.CountAsync(taskId, ct))); }
        catch (TaskNotFoundException ex) { return NotFound(new { error = ex.Message }); }
    }

    [HttpPost]
    public async Task<ActionResult<CommentResponse>> Create(int taskId, CreateCommentRequest request, CancellationToken ct)
    {
        try
        {
            var created = await _service.CreateAsync(taskId, request, ct);
            return CreatedAtAction(nameof(List), new { taskId }, created);
        }
        catch (TaskNotFoundException ex) { return NotFound(new { error = ex.Message }); }
        catch (InvalidCommentException ex) { return UnprocessableEntity(new { error = ex.Message }); }
    }

    [HttpDelete("{commentId:int}")]
    public async Task<IActionResult> Delete(int taskId, int commentId, CancellationToken ct)
    {
        try
        {
            await _service.DeleteAsync(taskId, commentId, ct);
            return NoContent();
        }
        catch (TaskNotFoundException ex) { return NotFound(new { error = ex.Message }); }
        catch (CommentNotFoundException ex) { return NotFound(new { error = ex.Message }); }
    }
}