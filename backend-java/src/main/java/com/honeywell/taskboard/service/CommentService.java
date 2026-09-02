package com.honeywell.taskboard.service;

import com.honeywell.taskboard.dto.CommentCreateRequest;
import com.honeywell.taskboard.dto.CommentResponse;
import java.util.List;

public interface CommentService {

    List<CommentResponse> list(int taskId);

    long count(int taskId);

    CommentResponse create(int taskId, CommentCreateRequest request);

    void delete(int taskId, int commentId);
}