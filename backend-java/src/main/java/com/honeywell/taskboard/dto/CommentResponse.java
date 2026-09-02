package com.honeywell.taskboard.dto;

import com.honeywell.taskboard.model.Comment;
import java.time.LocalDateTime;

public record CommentResponse(
        Integer id, Integer taskId, String author, String text, LocalDateTime createdAt) {

    public static CommentResponse from(Comment comment) {
        return new CommentResponse(comment.getId(), comment.getTaskId(), comment.getAuthor(),
                comment.getText(), comment.getCreatedAt());
    }
}