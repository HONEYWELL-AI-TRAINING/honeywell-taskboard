using TaskBoard.Api.Models;

namespace TaskBoard.Api.Repositories;

public interface ICommentRepository
{
    Task<IReadOnlyList<Comment>> ListAsync(int taskId, CancellationToken ct = default);
    Task<int> CountAsync(int taskId, CancellationToken ct = default);
    Task<Comment?> GetAsync(int taskId, int commentId, CancellationToken ct = default);
    Task<Comment> AddAsync(Comment comment, CancellationToken ct = default);
    Task DeleteAsync(Comment comment, CancellationToken ct = default);
}