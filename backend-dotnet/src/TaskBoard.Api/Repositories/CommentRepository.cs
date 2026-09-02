using Microsoft.EntityFrameworkCore;
using TaskBoard.Api.Data;
using TaskBoard.Api.Models;

namespace TaskBoard.Api.Repositories;

public class CommentRepository : ICommentRepository
{
    private readonly TaskBoardContext _db;

    public CommentRepository(TaskBoardContext db) => _db = db;

    public async Task<IReadOnlyList<Comment>> ListAsync(int taskId, CancellationToken ct = default) =>
        await _db.Comments.AsNoTracking().Where(comment => comment.TaskId == taskId)
            .OrderBy(comment => comment.Id).ToListAsync(ct);

    public Task<int> CountAsync(int taskId, CancellationToken ct = default) =>
        _db.Comments.CountAsync(comment => comment.TaskId == taskId, ct);

    public Task<Comment?> GetAsync(int taskId, int commentId, CancellationToken ct = default) =>
        _db.Comments.FirstOrDefaultAsync(comment => comment.TaskId == taskId && comment.Id == commentId, ct);

    public async Task<Comment> AddAsync(Comment comment, CancellationToken ct = default)
    {
        _db.Comments.Add(comment);
        await _db.SaveChangesAsync(ct);
        await _db.Entry(comment).ReloadAsync(ct);
        return comment;
    }

    public async Task DeleteAsync(Comment comment, CancellationToken ct = default)
    {
        _db.Comments.Remove(comment);
        await _db.SaveChangesAsync(ct);
    }
}