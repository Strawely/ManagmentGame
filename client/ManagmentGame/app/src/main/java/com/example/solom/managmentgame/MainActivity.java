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
            socket.on("success", new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    try {
                        handler.post(new Runnable() {
                            @Override
                            public void run() {
                                TextView result = findViewById(R.id.connectionResult);
                                result.setText("success");
                            }
                        });
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onTestConnectionClick(View view) {
        socket.connect();
//        socket.disconnect();
    }

    public void onEnterBtnClick(View view) {
        if(!socket.connected()) socket.connect();
        EditText loginEditText = findViewById(R.id.editTextLogin);
        socket.emit("register_player", loginEditText.getText(), 0);
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
