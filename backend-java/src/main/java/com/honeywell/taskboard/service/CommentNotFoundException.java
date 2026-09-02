package com.honeywell.taskboard.service;

public class CommentNotFoundException extends RuntimeException {
    public CommentNotFoundException(int id) {
        super("Comment " + id + " not found");
    }
}