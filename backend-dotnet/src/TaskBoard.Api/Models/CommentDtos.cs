using System.ComponentModel.DataAnnotations;

namespace TaskBoard.Api.Models;

public record CommentResponse(int Id, int TaskId, string Author, string Text, DateTime CreatedAt)
{
    public static CommentResponse From(Comment comment) =>
        new(comment.Id, comment.TaskId, comment.Author, comment.Text, comment.CreatedAt);
}

public record CommentCountResponse(int Count);

public class CreateCommentRequest
{
    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Author { get; set; } = string.Empty;

    [Required]
    [StringLength(500, MinimumLength = 1)]
    public string Text { get; set; } = string.Empty;
}