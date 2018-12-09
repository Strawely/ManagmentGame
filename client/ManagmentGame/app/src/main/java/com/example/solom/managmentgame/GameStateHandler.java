package com.example.solom.managmentgame;

public class GameStateHandler {

    private static Player player;

    public static Player getPlayer() {
        return player;
    }

    public static void setPlayer(Player player) {
        GameStateHandler.player = player;
    }
}
