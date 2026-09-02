package com.honeywell.taskboard.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

import com.honeywell.taskboard.dto.CommentCreateRequest;
import com.honeywell.taskboard.dto.CommentResponse;
import com.honeywell.taskboard.model.Comment;
import com.honeywell.taskboard.repository.CommentRepository;
import com.honeywell.taskboard.repository.TaskRepository;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class CommentServiceImplTest {

    @Mock
    private CommentRepository comments;

    @Mock
    private TaskRepository tasks;

    private CommentServiceImpl service;

    @BeforeEach
    void setUp() {
        service = new CommentServiceImpl(comments, tasks);
    }

    @Test
    void listReturnsCommentsOldestFirst() {
        when(tasks.existsById(1)).thenReturn(true);
        when(comments.findByTaskIdOrderByIdAsc(1)).thenReturn(List.of(
                comment(1, "First"), comment(2, "Second")));

        List<CommentResponse> result = service.list(1);

        assertThat(result).extracting(CommentResponse::text).containsExactly("First", "Second");
    }

    @Test
    void createRejectsWhitespaceOnlyText() {
        assertThatThrownBy(() -> service.create(1, new CommentCreateRequest("Sam", "   ")))
                .isInstanceOf(InvalidCommentException.class);
    }

    @Test
    void deleteThrowsWhenCommentIsMissing() {
        when(tasks.existsById(1)).thenReturn(true);
        when(comments.findByIdAndTaskId(9, 1)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.delete(1, 9)).isInstanceOf(CommentNotFoundException.class);
    }

    private static Comment comment(int id, String text) {
        Comment comment = new Comment();
        comment.setId(id);
        comment.setTaskId(1);
        comment.setAuthor("Sam");
        comment.setText(text);
        return comment;
    }
}