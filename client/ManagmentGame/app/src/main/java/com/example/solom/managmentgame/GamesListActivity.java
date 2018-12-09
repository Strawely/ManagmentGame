package com.example.solom.managmentgame;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import com.github.nkzawa.socketio.client.Ack;
import com.github.nkzawa.socketio.client.Socket;

import org.json.JSONArray;
import org.json.JSONException;

import java.util.ArrayList;

public class GamesListActivity extends Activity {

    private Socket socket;
    private Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        try {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_games_list);
            socket = SocketHandler.getSocket();
            updateGamesList();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    private void updateGamesList(){
        try {
            final ArrayList<String> gamesList = new ArrayList<>();
            ListView list = (ListView)findViewById(R.id.gamesList);
            final ArrayAdapter<String> gamesNamesAdapter =  new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, gamesList);
            list.setAdapter(gamesNamesAdapter);
            handler.post(new Runnable() {
                @Override
                public void run() {
                    socket.emit("get_games_list", null, new Ack() {
                        @Override
                        public void call(Object... args) {
                            try {
                                gamesList.clear();
                                JSONArray jsonArgs = (JSONArray) args[0];
                                String[] gamesNames = new String[jsonArgs.length()];
                                for (int i = 0; i < jsonArgs.length(); i++) {
                                    gamesList.add(jsonArgs.getJSONArray(i).getString(5));
                                    handler.post(new Runnable() {
                                        @Override
                                        public void run() {
                                            gamesNamesAdapter.notifyDataSetChanged();
                                        }
                                    });
                                }
                                fillGamesList(gamesNames);
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    handler.postDelayed(this, 2000);
                }
            });

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void onGetGamesClick(View view) {

    }

    private void fillGamesList(String[] gamesNames){
        try {

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
