package com.honeywell.taskboard.service;

import com.honeywell.taskboard.dto.CommentCreateRequest;
import com.honeywell.taskboard.dto.CommentResponse;
import com.honeywell.taskboard.model.Comment;
import com.honeywell.taskboard.repository.CommentRepository;
import com.honeywell.taskboard.repository.TaskRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class CommentServiceImpl implements CommentService {

    private final CommentRepository comments;
    private final TaskRepository tasks;

    public CommentServiceImpl(CommentRepository comments, TaskRepository tasks) {
        this.comments = comments;
        this.tasks = tasks;
    }

    @Override
    @Transactional(readOnly = true)
    public List<CommentResponse> list(int taskId) {
        requireTask(taskId);
        return comments.findByTaskIdOrderByIdAsc(taskId).stream().map(CommentResponse::from).toList();
    }

    @Override
    @Transactional(readOnly = true)
    public long count(int taskId) {
        requireTask(taskId);
        return comments.countByTaskId(taskId);
    }

    @Override
    public CommentResponse create(int taskId, CommentCreateRequest request) {
        validate(request);
        requireTask(taskId);
        Comment comment = new Comment();
        comment.setTaskId(taskId);
        comment.setAuthor(request.author());
        comment.setText(request.text());
        return CommentResponse.from(comments.saveAndFlush(comment));
    }

    @Override
    public void delete(int taskId, int commentId) {
        requireTask(taskId);
        Comment comment = comments.findByIdAndTaskId(commentId, taskId)
                .orElseThrow(() -> new CommentNotFoundException(commentId));
        comments.delete(comment);
    }

    private void requireTask(int taskId) {
        if (!tasks.existsById(taskId)) {
            throw new TaskNotFoundException(taskId);
        }
    }

    private static void validate(CommentCreateRequest request) {
        if (request.author() == null || request.author().isEmpty() || request.author().length() > 100 ||
                request.text() == null || request.text().isBlank() || request.text().length() > 500) {
            throw new InvalidCommentException();
        }
    }
}