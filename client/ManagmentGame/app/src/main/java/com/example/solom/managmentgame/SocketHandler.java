package com.example.solom.managmentgame;

import com.github.nkzawa.socketio.client.Socket;

public class SocketHandler {
    private static Socket socket;

    public static Socket getSocket(){
        return socket;
    }

    public static void setSocket(Socket socket){
        SocketHandler.socket = socket;
    }
}
