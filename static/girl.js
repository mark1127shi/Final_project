const modelURL =
  "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json";

(async () => {

  const container = document.getElementById("live2d-container");
  const canvas = document.getElementById("live2d");

  /* pixi */
  const app = new PIXI.Application({
    view: canvas,
    resizeTo: container,
    backgroundAlpha: 0,
    autoStart: true
  });

  /* const model */
  const model = await PIXI.live2d.Live2DModel.from(modelURL);

  model.scale.set(0.25);
  model.anchor.set(0.5, 1);
  model.x = app.screen.width / 2;
  model.y = app.screen.height - model.height * model.scale.y * 0.6;


  model.interactive = true;
  model.buttonMode = true;
  model.interactiveChildren = true;

  app.stage.interactive = true;
  app.stage.hitArea = app.screen;

  app.stage.addChild(model);

  /* const bubble */
  const bubble = new PIXI.Container();
  bubble.visible = false;

  const bubbleBg = new PIXI.Graphics()
    .beginFill(0xffffff, 0.9)
    .drawRoundedRect(0, 0, 220, 80, 16)
    .endFill();

  const bubbleText = new PIXI.Text("", {
    fontSize: 16,
    fill: 0x333333,
    wordWrap: true,
    wordWrapWidth: 190
  });

  bubbleText.position.set(15, 15);

  const tail = new PIXI.Graphics()
    .beginFill(0xffffff, 0.9)
    .drawPolygon([0,0, 20,20, 40,0])
    .endFill();
  tail.position.set(70, 75);

  bubble.addChild(bubbleBg, bubbleText, tail);
  app.stage.addChild(bubble);

  app.ticker.add(() => {
    bubble.x = model.x - 110;
    bubble.y = model.y - model.height * model.scale.y - 40;
  });

  /* speaking part */
  const texts = [
    "Hey! ",
    "That tickles!",
    "Please be gentle ",
    "Hi there!",
    "Do you need help?",
    "やめて〜",
    "くすぐったい！",
    "やさしくしてね ",
    "こんにちは！",
    "何か用？"
  ];

  const jp_texts = [  //from anime
    "えっ？！ (Eh?!)",
    "えーと… (Eeto...)",
    "やばい！ (Yabai!)",
    "もう...",
  ]

  let timer = null;

  model.on("hit", (areas) => {
    if (areas.includes("head")) {
      bubbleText.text = texts[Math.floor(Math.random() * texts.length)];
      bubble.visible = true;
      clearTimeout(timer);
      timer = setTimeout(() => bubble.visible = false, 2500);
      model.expression();
    }

    if (areas.includes("body")) {
      bubbleText.text = jp_texts[Math.floor(Math.random() * jp_texts.length)];
      bubble.visible = true;
      clearTimeout(timer);
      timer = setTimeout(() => bubble.visible = false, 2500);
      model.motion("tap_body");
    }

    if (areas.includes('mouth')){
      model.motion("shake");
    }
  });

  model.on("pointertap", () => {
    console.log("MODEL CLICKED ");
  });

  /* drag the container as a whole part only instead of the character */
  let containerDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  container.addEventListener("pointerdown", (e) => {
    //Only drag when Shift is held
    if (!e.shiftKey) return;

    containerDragging = true;
    offsetX = e.clientX - container.offsetLeft;
    offsetY = e.clientY - container.offsetTop;

    container.setPointerCapture(e.pointerId);
  });

  container.addEventListener("pointermove", (e) => {
    if (!containerDragging) return;

    container.style.left = `${e.clientX - offsetX}px`;
    container.style.top = `${e.clientY - offsetY}px`;
    container.style.right = "auto";
    container.style.bottom = "auto";
  });

  container.addEventListener("pointerup", () => {
    containerDragging = false;
  });

  container.addEventListener("pointercancel", () => {
    containerDragging = false;
  });

})();
