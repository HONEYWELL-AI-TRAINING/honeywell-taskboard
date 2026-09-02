using TaskBoard.Api.Models;
using TaskBoard.Api.Repositories;

namespace TaskBoard.Api.Services;

public class CommentService : ICommentService
{
    private readonly ICommentRepository _comments;
    private readonly ITaskRepository _tasks;

    public CommentService(ICommentRepository comments, ITaskRepository tasks)
    {
        _comments = comments;
        _tasks = tasks;
    }

    public async Task<IReadOnlyList<CommentResponse>> ListAsync(int taskId, CancellationToken ct = default)
    {
        await GetTaskAsync(taskId, ct);
        return (await _comments.ListAsync(taskId, ct)).Select(CommentResponse.From).ToList();
    }

    public async Task<int> CountAsync(int taskId, CancellationToken ct = default)
    {
        await GetTaskAsync(taskId, ct);
        return await _comments.CountAsync(taskId, ct);
    }

    public async Task<CommentResponse> CreateAsync(int taskId, CreateCommentRequest request, CancellationToken ct = default)
    {
        Validate(request);
        await GetTaskAsync(taskId, ct);
        var comment = await _comments.AddAsync(new Comment
        {
            TaskId = taskId,
            Author = request.Author,
            Text = request.Text,
        }, ct);
        return CommentResponse.From(comment);
    }

    public async Task DeleteAsync(int taskId, int commentId, CancellationToken ct = default)
    {
        await GetTaskAsync(taskId, ct);
        var comment = await _comments.GetAsync(taskId, commentId, ct)
            ?? throw new CommentNotFoundException(commentId);
        await _comments.DeleteAsync(comment, ct);
    }

    private async Task GetTaskAsync(int taskId, CancellationToken ct) =>
        _ = await _tasks.GetAsync(taskId, ct) ?? throw new TaskNotFoundException(taskId);

    private static void Validate(CreateCommentRequest request)
    {
        if (string.IsNullOrEmpty(request.Author) || request.Author.Length > 100 ||
            string.IsNullOrWhiteSpace(request.Text) || request.Text.Length > 500)
            throw new InvalidCommentException();
    }
}