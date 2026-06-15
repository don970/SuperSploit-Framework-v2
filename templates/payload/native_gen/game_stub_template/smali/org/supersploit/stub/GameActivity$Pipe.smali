.class Lorg/supersploit/stub/GameActivity$Pipe;
.super Ljava/lang/Object;
.source "GameActivity.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lorg/supersploit/stub/GameActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = "Pipe"
.end annotation


# instance fields
.field gapY:I

.field x:I


# direct methods
.method constructor <init>(Lorg/supersploit/stub/GameActivity;II)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x0,
            0x0
        }
        names = {
            null,
            null,
            null
        }
    .end annotation

    .line 152
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput p2, p0, Lorg/supersploit/stub/GameActivity$Pipe;->x:I

    iput p3, p0, Lorg/supersploit/stub/GameActivity$Pipe;->gapY:I

    return-void
.end method
