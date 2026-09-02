package com.honeywell.taskboard.web;

import com.honeywell.taskboard.dto.CommentCountResponse;
import com.honeywell.taskboard.dto.CommentCreateRequest;
import com.honeywell.taskboard.dto.CommentResponse;
import com.honeywell.taskboard.service.CommentService;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/tasks/{taskId}/comments")
public class CommentController {

    private final CommentService service;

    public CommentController(CommentService service) {
        this.service = service;
    }

    @GetMapping
    public List<CommentResponse> list(@PathVariable int taskId) {
        return service.list(taskId);
    }

    @GetMapping("/count")
    public CommentCountResponse count(@PathVariable int taskId) {
        return new CommentCountResponse(service.count(taskId));
    }

    @PostMapping
    public ResponseEntity<CommentResponse> create(
            @PathVariable int taskId, @Valid @RequestBody CommentCreateRequest request) {
        CommentResponse created = service.create(taskId, request);
        return ResponseEntity.created(URI.create("/api/tasks/" + taskId + "/comments/" + created.id()))
                .body(created);
    }

    @DeleteMapping("/{commentId}")
    public ResponseEntity<Void> delete(@PathVariable int taskId, @PathVariable int commentId) {
        service.delete(taskId, commentId);
        return ResponseEntity.noContent().build();
    }
}