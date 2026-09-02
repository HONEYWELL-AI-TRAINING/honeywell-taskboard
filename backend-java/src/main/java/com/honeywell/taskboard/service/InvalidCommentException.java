package com.honeywell.taskboard.service;

public class InvalidCommentException extends RuntimeException {
    public InvalidCommentException() {
        super("Comment author and text are invalid");
    }
}