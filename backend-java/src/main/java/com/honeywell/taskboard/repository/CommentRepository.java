package com.honeywell.taskboard.repository;

import com.honeywell.taskboard.model.Comment;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommentRepository extends JpaRepository<Comment, Integer> {

    List<Comment> findByTaskIdOrderByIdAsc(int taskId);

    long countByTaskId(int taskId);

    Optional<Comment> findByIdAndTaskId(int id, int taskId);
}