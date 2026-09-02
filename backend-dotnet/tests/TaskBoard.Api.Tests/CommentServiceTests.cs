using Moq;
using TaskBoard.Api.Models;
using TaskBoard.Api.Repositories;
using TaskBoard.Api.Services;
using Xunit;

namespace TaskBoard.Api.Tests;

public class CommentServiceTests
{
    private readonly Mock<ICommentRepository> _comments = new();
    private readonly Mock<ITaskRepository> _tasks = new();
    private readonly CommentService _sut;

    public CommentServiceTests() => _sut = new CommentService(_comments.Object, _tasks.Object);

    [Fact]
    public async Task ListAsync_ReturnsCommentsOldestFirst()
    {
        _tasks.Setup(r => r.GetAsync(1, It.IsAny<CancellationToken>())).ReturnsAsync(new TaskItem());
        _comments.Setup(r => r.ListAsync(1, It.IsAny<CancellationToken>())).ReturnsAsync(new List<Comment>
        {
            new() { Id = 1, TaskId = 1, Author = "Sam", Text = "First" },
            new() { Id = 2, TaskId = 1, Author = "Priya", Text = "Second" },
        });

        var result = await _sut.ListAsync(1);

        Assert.Equal(["First", "Second"], result.Select(comment => comment.Text));
    }

    [Fact]
    public async Task CreateAsync_RejectsWhitespaceOnlyText()
    {
        _tasks.Setup(r => r.GetAsync(1, It.IsAny<CancellationToken>())).ReturnsAsync(new TaskItem());

        await Assert.ThrowsAsync<InvalidCommentException>(() =>
            _sut.CreateAsync(1, new CreateCommentRequest { Author = "Sam", Text = "   " }));
    }

    [Fact]
    public async Task DeleteAsync_ThrowsWhenCommentIsMissing()
    {
        _tasks.Setup(r => r.GetAsync(1, It.IsAny<CancellationToken>())).ReturnsAsync(new TaskItem());
        _comments.Setup(r => r.GetAsync(1, 9, It.IsAny<CancellationToken>())).ReturnsAsync((Comment?)null);

        await Assert.ThrowsAsync<CommentNotFoundException>(() => _sut.DeleteAsync(1, 9));
    }
}