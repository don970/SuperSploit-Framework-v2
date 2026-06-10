.class Lorg/supersploit/stub/GameActivity$GameView;
.super Landroid/view/View;
.source "GameActivity.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lorg/supersploit/stub/GameActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = "GameView"
.end annotation


# instance fields
.field private birdV:I

.field private birdY:I

.field private frameCount:I

.field private gameOver:Z

.field private gameStarted:Z

.field private gravity:I

.field private jumpStrength:I

.field private paint:Landroid/graphics/Paint;

.field private pipes:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lorg/supersploit/stub/GameActivity$Pipe;",
            ">;"
        }
    .end annotation
.end field

.field private random:Ljava/util/Random;

.field private score:I

.field final synthetic this$0:Lorg/supersploit/stub/GameActivity;


# direct methods
.method public constructor <init>(Lorg/supersploit/stub/GameActivity;Landroid/content/Context;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x0
        }
        names = {
            null,
            null
        }
    .end annotation

    .line 50
    iput-object p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->this$0:Lorg/supersploit/stub/GameActivity;

    .line 51
    invoke-direct {p0, p2}, Landroid/view/View;-><init>(Landroid/content/Context;)V

    .line 38
    new-instance p1, Landroid/graphics/Paint;

    invoke-direct {p1}, Landroid/graphics/Paint;-><init>()V

    iput-object p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    .line 39
    const/16 p1, 0x1f4

    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    .line 40
    const/4 p1, 0x0

    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    .line 41
    const/4 p2, 0x2

    iput p2, p0, Lorg/supersploit/stub/GameActivity$GameView;->gravity:I

    .line 42
    const/16 p2, -0x1e

    iput p2, p0, Lorg/supersploit/stub/GameActivity$GameView;->jumpStrength:I

    .line 43
    iput-boolean p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    .line 44
    iput-boolean p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameStarted:Z

    .line 45
    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->score:I

    .line 46
    new-instance p2, Ljava/util/ArrayList;

    invoke-direct {p2}, Ljava/util/ArrayList;-><init>()V

    iput-object p2, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    .line 47
    new-instance p2, Ljava/util/Random;

    invoke-direct {p2}, Ljava/util/Random;-><init>()V

    iput-object p2, p0, Lorg/supersploit/stub/GameActivity$GameView;->random:Ljava/util/Random;

    .line 48
    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->frameCount:I

    .line 52
    return-void
.end method


# virtual methods
.method protected onDraw(Landroid/graphics/Canvas;)V
    .locals 13

    .line 56
    invoke-super/range {p0 .. p1}, Landroid/view/View;->onDraw(Landroid/graphics/Canvas;)V

    .line 59
    const-string v1, "#70C5CE"

    invoke-static {v1}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v1

    invoke-virtual {p1, v1}, Landroid/graphics/Canvas;->drawColor(I)V

    .line 61
    iget-boolean v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameStarted:Z

    const/high16 v6, 0x42c80000    # 100.0f

    const/4 v7, -0x1

    if-nez v1, :cond_0

    .line 62
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7}, Landroid/graphics/Paint;->setColor(I)V

    .line 63
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    invoke-virtual {v1, v6}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 64
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Align;->CENTER:Landroid/graphics/Paint$Align;

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextAlign(Landroid/graphics/Paint$Align;)V

    .line 65
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getWidth()I

    move-result v1

    div-int/lit8 v1, v1, 0x2

    int-to-float v1, v1

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v2

    div-int/lit8 v2, v2, 0x2

    int-to-float v2, v2

    iget-object v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const-string v4, "TAP TO START"

    invoke-virtual {p1, v4, v1, v2, v3}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 66
    return-void

    .line 69
    :cond_0
    iget-boolean v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    const/16 v8, 0x64

    if-nez v1, :cond_8

    .line 71
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    iget v2, p0, Lorg/supersploit/stub/GameActivity$GameView;->gravity:I

    add-int/2addr v1, v2

    iput v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    .line 72
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    iget v2, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    add-int/2addr v1, v2

    iput v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    .line 74
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v2

    const/4 v9, 0x1

    if-gt v1, v2, :cond_1

    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    if-gez v1, :cond_2

    :cond_1
    iput-boolean v9, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    .line 77
    :cond_2
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->frameCount:I

    rem-int/2addr v1, v8

    if-nez v1, :cond_3

    .line 78
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->random:Ljava/util/Random;

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v2

    add-int/lit16 v2, v2, -0x258

    invoke-virtual {v1, v2}, Ljava/util/Random;->nextInt(I)I

    move-result v1

    add-int/lit16 v1, v1, 0x12c

    .line 79
    iget-object v2, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    new-instance v3, Lorg/supersploit/stub/GameActivity$Pipe;

    iget-object v4, p0, Lorg/supersploit/stub/GameActivity$GameView;->this$0:Lorg/supersploit/stub/GameActivity;

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getWidth()I

    move-result v5

    invoke-direct {v3, v4, v5, v1}, Lorg/supersploit/stub/GameActivity$Pipe;-><init>(Lorg/supersploit/stub/GameActivity;II)V

    invoke-interface {v2, v3}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 81
    :cond_3
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->frameCount:I

    add-int/2addr v1, v9

    iput v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->frameCount:I

    .line 84
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->size()I

    move-result v1

    sub-int/2addr v1, v9

    move v10, v1

    :goto_0
    if-ltz v10, :cond_8

    .line 85
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    invoke-interface {v1, v10}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v1

    move-object v11, v1

    check-cast v11, Lorg/supersploit/stub/GameActivity$Pipe;

    .line 86
    iget v1, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    add-int/lit8 v1, v1, -0xa

    iput v1, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    .line 88
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const-string v2, "#75BF2F"

    invoke-static {v2}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I

    move-result v2

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 90
    iget v1, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    int-to-float v1, v1

    iget v2, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    add-int/lit16 v2, v2, 0x96

    int-to-float v3, v2

    iget v2, v11, Lorg/supersploit/stub/GameActivity$Pipe;->gapY:I

    add-int/lit16 v2, v2, -0xc8

    int-to-float v4, v2

    iget-object v5, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/4 v2, 0x0

    move-object v0, p1

    invoke-virtual/range {v0 .. v5}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    .line 92
    iget v0, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    int-to-float v1, v0

    iget v0, v11, Lorg/supersploit/stub/GameActivity$Pipe;->gapY:I

    add-int/lit16 v0, v0, 0xc8

    int-to-float v2, v0

    iget v0, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    add-int/lit16 v0, v0, 0x96

    int-to-float v3, v0

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v0

    int-to-float v4, v0

    iget-object v5, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    move-object v0, p1

    invoke-virtual/range {v0 .. v5}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    .line 95
    new-instance v1, Landroid/graphics/Rect;

    iget v2, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    iget v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    add-int/lit8 v3, v3, 0x3c

    const/16 v4, 0xa0

    invoke-direct {v1, v8, v2, v4, v3}, Landroid/graphics/Rect;-><init>(IIII)V

    .line 96
    new-instance v2, Landroid/graphics/Rect;

    iget v3, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    iget v4, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    add-int/lit16 v4, v4, 0x96

    iget v5, v11, Lorg/supersploit/stub/GameActivity$Pipe;->gapY:I

    add-int/lit16 v5, v5, -0xc8

    const/4 v12, 0x0

    invoke-direct {v2, v3, v12, v4, v5}, Landroid/graphics/Rect;-><init>(IIII)V

    invoke-static {v1, v2}, Landroid/graphics/Rect;->intersects(Landroid/graphics/Rect;Landroid/graphics/Rect;)Z

    move-result v2

    if-nez v2, :cond_4

    new-instance v2, Landroid/graphics/Rect;

    iget v3, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    iget v4, v11, Lorg/supersploit/stub/GameActivity$Pipe;->gapY:I

    add-int/lit16 v4, v4, 0xc8

    iget v5, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    add-int/lit16 v5, v5, 0x96

    .line 97
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v12

    invoke-direct {v2, v3, v4, v5, v12}, Landroid/graphics/Rect;-><init>(IIII)V

    invoke-static {v1, v2}, Landroid/graphics/Rect;->intersects(Landroid/graphics/Rect;Landroid/graphics/Rect;)Z

    move-result v1

    if-eqz v1, :cond_5

    .line 98
    :cond_4
    iput-boolean v9, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    .line 101
    :cond_5
    iget v1, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    if-ne v1, v8, :cond_6

    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->score:I

    add-int/2addr v1, v9

    iput v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->score:I

    .line 103
    :cond_6
    iget v1, v11, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    const/16 v2, -0x96

    if-ge v1, v2, :cond_7

    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    invoke-interface {v1, v10}, Ljava/util/List;->remove(I)Ljava/lang/Object;

    .line 84
    :cond_7
    add-int/lit8 v10, v10, -0x1

    goto/16 :goto_0

    .line 108
    :cond_8
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/16 v2, -0x100

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 109
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    add-int/lit8 v1, v1, 0x1e

    int-to-float v1, v1

    const/high16 v2, 0x41f00000    # 30.0f

    iget-object v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/high16 v4, 0x43020000    # 130.0f

    invoke-virtual {p1, v4, v1, v2, v3}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 112
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7}, Landroid/graphics/Paint;->setColor(I)V

    .line 113
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/high16 v2, 0x42a00000    # 80.0f

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 114
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Align;->LEFT:Landroid/graphics/Paint$Align;

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextAlign(Landroid/graphics/Paint$Align;)V

    .line 115
    iget v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->score:I

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Score: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/high16 v2, 0x42480000    # 50.0f

    iget-object v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    invoke-virtual {p1, v1, v2, v6, v3}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 117
    iget-boolean v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    if-eqz v1, :cond_9

    .line 118
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Align;->CENTER:Landroid/graphics/Paint$Align;

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextAlign(Landroid/graphics/Paint$Align;)V

    .line 119
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/high16 v2, 0x42f00000    # 120.0f

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 120
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getWidth()I

    move-result v1

    div-int/lit8 v1, v1, 0x2

    int-to-float v1, v1

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v2

    div-int/lit8 v2, v2, 0x2

    int-to-float v2, v2

    iget-object v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const-string v4, "GAME OVER"

    invoke-virtual {p1, v4, v1, v2, v3}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 121
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const/high16 v2, 0x42700000    # 60.0f

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 122
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getWidth()I

    move-result v1

    div-int/lit8 v1, v1, 0x2

    int-to-float v1, v1

    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->getHeight()I

    move-result v2

    div-int/lit8 v2, v2, 0x2

    add-int/2addr v2, v8

    int-to-float v2, v2

    iget-object v3, p0, Lorg/supersploit/stub/GameActivity$GameView;->paint:Landroid/graphics/Paint;

    const-string v4, "Tap to restart"

    invoke-virtual {p1, v4, v1, v2, v3}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    goto :goto_1

    .line 124
    :cond_9
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->invalidate()V

    .line 126
    :goto_1
    return-void
.end method

.method public onTouchEvent(Landroid/view/MotionEvent;)Z
    .locals 2

    .line 130
    invoke-virtual {p1}, Landroid/view/MotionEvent;->getAction()I

    move-result p1

    const/4 v0, 0x1

    if-nez p1, :cond_2

    .line 131
    iget-boolean p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    if-eqz p1, :cond_0

    .line 132
    const/16 p1, 0x1f4

    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdY:I

    .line 133
    const/4 p1, 0x0

    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    .line 134
    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->score:I

    .line 135
    iget-object v1, p0, Lorg/supersploit/stub/GameActivity$GameView;->pipes:Ljava/util/List;

    invoke-interface {v1}, Ljava/util/List;->clear()V

    .line 136
    iput-boolean p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameOver:Z

    .line 137
    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->frameCount:I

    .line 138
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->invalidate()V

    goto :goto_0

    .line 139
    :cond_0
    iget-boolean p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameStarted:Z

    if-nez p1, :cond_1

    .line 140
    iput-boolean v0, p0, Lorg/supersploit/stub/GameActivity$GameView;->gameStarted:Z

    .line 141
    invoke-virtual {p0}, Lorg/supersploit/stub/GameActivity$GameView;->invalidate()V

    goto :goto_0

    .line 143
    :cond_1
    iget p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->jumpStrength:I

    iput p1, p0, Lorg/supersploit/stub/GameActivity$GameView;->birdV:I

    .line 146
    :cond_2
    :goto_0
    return v0
.end method
