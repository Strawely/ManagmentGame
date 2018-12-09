package com.example.solom.managmentgame;

public class Player {
    private int id;
    private String nickname;
    private int avatar;

    public Player(int id, String nickname, int avatar) {
        this.id = id;
        this.nickname = nickname;
        this.avatar = avatar;
    }

    public int getId() {
        return id;
    }

    public String getNickname() {
        return nickname;
    }

    public int getAvatar() {
        return avatar;
    }
}
