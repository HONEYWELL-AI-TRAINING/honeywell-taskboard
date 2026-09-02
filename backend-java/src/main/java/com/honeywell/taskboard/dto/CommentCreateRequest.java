package com.honeywell.taskboard.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CommentCreateRequest(
        @NotNull @Size(min = 1, max = 100) String author,
        @NotNull @Size(min = 1, max = 500) String text) {
}