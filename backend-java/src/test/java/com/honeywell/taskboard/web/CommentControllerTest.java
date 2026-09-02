package com.honeywell.taskboard.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.honeywell.taskboard.dto.CommentCreateRequest;
import com.honeywell.taskboard.dto.CommentResponse;
import com.honeywell.taskboard.service.CommentNotFoundException;
import com.honeywell.taskboard.service.CommentService;
import com.honeywell.taskboard.service.InvalidCommentException;
import com.honeywell.taskboard.service.TaskNotFoundException;
import java.time.LocalDateTime;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

@ExtendWith(MockitoExtension.class)
class CommentControllerTest {

    @Mock
    private CommentService service;

    private MockMvc mvc;

    @BeforeEach
    void setUp() {
        mvc = MockMvcBuilders.standaloneSetup(new CommentController(service))
                .setControllerAdvice(new ApiExceptionHandler())
                .build();
    }

    @Test
    void countReturnsCommentsForExistingTask() throws Exception {
        when(service.count(1)).thenReturn(2L);

        mvc.perform(get("/api/tasks/1/comments/count"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.count").value(2));
    }

    @Test
    void listReturns404WhenTaskIsMissing() throws Exception {
        when(service.list(9)).thenThrow(new TaskNotFoundException(9));

        mvc.perform(get("/api/tasks/9/comments"))
                .andExpect(status().isNotFound());
    }

    @Test
    void countReturns404WhenTaskIsMissing() throws Exception {
        when(service.count(9)).thenThrow(new TaskNotFoundException(9));

        mvc.perform(get("/api/tasks/9/comments/count"))
                .andExpect(status().isNotFound());
    }

    @Test
    void createReturnsCreatedComment() throws Exception {
        when(service.create(any(Integer.class), any(CommentCreateRequest.class)))
                .thenReturn(new CommentResponse(3, 1, "Sam", "Note", LocalDateTime.now()));

        mvc.perform(post("/api/tasks/1/comments")
                        .contentType("application/json")
                        .content("{\"author\":\"Sam\",\"text\":\"Note\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(3));
    }

    @Test
    void createReturns422WhenTextIsBlank() throws Exception {
        when(service.create(any(Integer.class), any(CommentCreateRequest.class)))
            .thenThrow(new InvalidCommentException());

        mvc.perform(post("/api/tasks/1/comments")
                        .contentType("application/json")
                        .content("{\"author\":\"Sam\",\"text\":\"   \"}"))
                .andExpect(status().isUnprocessableEntity());
    }

            @Test
            void createReturns404WhenTaskIsMissing() throws Exception {
            when(service.create(any(Integer.class), any(CommentCreateRequest.class)))
                .thenThrow(new TaskNotFoundException(9));

            mvc.perform(post("/api/tasks/9/comments")
                    .contentType("application/json")
                    .content("{\"author\":\"Sam\",\"text\":\"Note\"}"))
                .andExpect(status().isNotFound());
            }

    @Test
    void deleteReturns404WhenCommentIsMissing() throws Exception {
        doThrow(new CommentNotFoundException(9)).when(service).delete(1, 9);

        mvc.perform(delete("/api/tasks/1/comments/9"))
                .andExpect(status().isNotFound());
    }

    @Test
    void deleteReturns404WhenTaskIsMissing() throws Exception {
        doThrow(new TaskNotFoundException(9)).when(service).delete(9, 1);

        mvc.perform(delete("/api/tasks/9/comments/1"))
                .andExpect(status().isNotFound());
    }
}