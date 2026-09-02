using Microsoft.AspNetCore.Mvc;
using Moq;
using TaskBoard.Api.Controllers;
using TaskBoard.Api.Models;
using TaskBoard.Api.Services;
using Xunit;

namespace TaskBoard.Api.Tests;

public class CommentsControllerTests
{
    private readonly Mock<ICommentService> _service = new();
    private readonly CommentsController _sut;

    public CommentsControllerTests() => _sut = new CommentsController(_service.Object);

    [Fact]
    public async Task Count_ReturnsOkForExistingTask()
    {
        _service.Setup(s => s.CountAsync(1, It.IsAny<CancellationToken>())).ReturnsAsync(2);

        var action = await _sut.Count(1, CancellationToken.None);

        var ok = Assert.IsType<OkObjectResult>(action.Result);
        Assert.Equal(2, ((CommentCountResponse)ok.Value!).Count);
    }

    [Fact]
    public async Task List_ReturnsNotFoundWhenTaskIsMissing()
    {
        _service.Setup(s => s.ListAsync(9, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskNotFoundException(9));

        var action = await _sut.List(9, CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(action.Result);
    }

    [Fact]
    public async Task Count_ReturnsNotFoundWhenTaskIsMissing()
    {
        _service.Setup(s => s.CountAsync(9, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskNotFoundException(9));

        var action = await _sut.Count(9, CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(action.Result);
    }

    [Fact]
    public async Task Create_ReturnsCreatedComment()
    {
        var comment = new CommentResponse(3, 1, "Sam", "Note", DateTime.UtcNow);
        _service.Setup(s => s.CreateAsync(1, It.IsAny<CreateCommentRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(comment);

        var action = await _sut.Create(1, new CreateCommentRequest { Author = "Sam", Text = "Note" }, CancellationToken.None);

        var created = Assert.IsType<CreatedAtActionResult>(action.Result);
        Assert.Equal(3, ((CommentResponse)created.Value!).Id);
    }

    [Fact]
    public async Task Create_ReturnsUnprocessableEntityForInvalidComment()
    {
        _service.Setup(s => s.CreateAsync(1, It.IsAny<CreateCommentRequest>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidCommentException());

        var action = await _sut.Create(1, new CreateCommentRequest { Author = "Sam", Text = "   " }, CancellationToken.None);

        Assert.IsType<UnprocessableEntityObjectResult>(action.Result);
    }

    [Fact]
    public async Task Create_ReturnsNotFoundWhenTaskIsMissing()
    {
        _service.Setup(s => s.CreateAsync(9, It.IsAny<CreateCommentRequest>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskNotFoundException(9));

        var action = await _sut.Create(9, new CreateCommentRequest { Author = "Sam", Text = "Note" }, CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(action.Result);
    }

    [Fact]
    public async Task Delete_ReturnsNotFoundWhenCommentIsMissing()
    {
        _service.Setup(s => s.DeleteAsync(1, 9, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new CommentNotFoundException(9));

        var result = await _sut.Delete(1, 9, CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task Delete_ReturnsNotFoundWhenTaskIsMissing()
    {
        _service.Setup(s => s.DeleteAsync(9, 1, It.IsAny<CancellationToken>()))
            .ThrowsAsync(new TaskNotFoundException(9));

        var result = await _sut.Delete(9, 1, CancellationToken.None);

        Assert.IsType<NotFoundObjectResult>(result);
    }
}