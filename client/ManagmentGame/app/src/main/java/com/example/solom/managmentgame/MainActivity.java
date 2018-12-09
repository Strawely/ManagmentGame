package com.example.solom.managmentgame;

import android.content.Intent;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import com.github.nkzawa.emitter.Emitter;
import com.github.nkzawa.socketio.client.IO;
import com.github.nkzawa.socketio.client.Socket;

import java.net.URISyntaxException;

public class MainActivity extends AppCompatActivity {

    private Socket socket;
    private Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initSocket();
    }

    private void initSocket(){
        try {
            socket = IO.socket("http://10.0.3.2:5000");
            socket.connect();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onEnterBtnClick(View view) {
        Intent intent = new Intent(this, AuthActivity.class);
        SocketHandler.setSocket(socket);
        startActivity(intent);
    }

    public void onPlayBtnClick(View view) {
        try {
            if(!socket.connected()) socket.connect();
            Intent intent = new Intent(this, GamesListActivity.class);
            SocketHandler.setSocket(socket);
            startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
