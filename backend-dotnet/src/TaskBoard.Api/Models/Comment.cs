namespace TaskBoard.Api.Models;

public class Comment
{
    public int Id { get; set; }
    public int TaskId { get; set; }
    public string Author { get; set; } = string.Empty;
    public string Text { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}