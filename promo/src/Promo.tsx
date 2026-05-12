import type { FC } from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { COLORS, FONT_STACK, MONO_STACK } from "./theme";

export const FPS = 30;
export const DURATION = 60 * FPS; // 1800

// Scene start frames
const T_HOOK = 0;        // 0:00 — 0:03
const T_PAIN = 3 * FPS;  // 0:03 — 0:08
const T_REVEAL = 8 * FPS;  // 0:08 — 0:13
const T_DEMO = 13 * FPS; // 0:13 — 0:30
const T_FEATS = 30 * FPS; // 0:30 — 0:42
const T_INSTALL = 42 * FPS; // 0:42 — 0:50
const T_CTA = 50 * FPS; // 0:50 — 1:00

// ─────────────────────────────────────────────────────────────
// shared helpers
// ─────────────────────────────────────────────────────────────

const ease = (t: number) => 1 - Math.pow(1 - t, 3);

const fadeIn = (frame: number, from: number, dur = 8) =>
  interpolate(frame, [from, from + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const fadeOut = (frame: number, until: number, dur = 8) =>
  interpolate(frame, [until - dur, until], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const popIn = (
  frame: number,
  from: number,
  fps: number,
  cfg = { damping: 12, stiffness: 110, mass: 0.6 },
) =>
  spring({
    frame: frame - from,
    fps,
    config: cfg,
  });

// ─────────────────────────────────────────────────────────────
// reusable bits
// ─────────────────────────────────────────────────────────────

const StarField: FC = () => {
  const frame = useCurrentFrame();
  const dots = Array.from({ length: 60 }, (_, i) => {
    const seed = (i * 9301 + 49297) % 233280;
    const x = (seed % 100) / 100;
    const y = ((seed * 7) % 100) / 100;
    const speed = 0.3 + ((seed * 3) % 100) / 200;
    const drift = ((frame * speed) % 1080) / 1080;
    const ty = (y + drift) % 1;
    const size = 1 + ((seed * 11) % 4);
    const alpha = 0.15 + ((seed * 13) % 50) / 100;
    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: `${x * 100}%`,
          top: `${ty * 100}%`,
          width: size,
          height: size,
          borderRadius: 999,
          background: COLORS.text,
          opacity: alpha,
        }}
      />
    );
  });
  return <>{dots}</>;
};

const RadialGlow: FC<{ color: string; x: string; y: string; size?: number; alpha?: number }> = ({
  color,
  x,
  y,
  size = 1400,
  alpha = 0.45,
}) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      width: size,
      height: size,
      transform: "translate(-50%, -50%)",
      background: `radial-gradient(circle, ${color}${Math.round(alpha * 255)
        .toString(16)
        .padStart(2, "0")} 0%, transparent 60%)`,
      filter: "blur(6px)",
    }}
  />
);

const Bg: FC<{ variant?: "dark" | "purple" | "pink" | "ink" }> = ({
  variant = "dark",
}) => {
  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <StarField />
      {variant === "purple" && (
        <>
          <RadialGlow color={COLORS.accent} x="20%" y="20%" />
          <RadialGlow color={COLORS.pink} x="85%" y="85%" alpha={0.35} />
        </>
      )}
      {variant === "pink" && (
        <>
          <RadialGlow color={COLORS.pink} x="50%" y="30%" alpha={0.6} />
          <RadialGlow color={COLORS.accent} x="50%" y="90%" alpha={0.35} />
        </>
      )}
      {variant === "ink" && (
        <RadialGlow color={COLORS.accent} x="50%" y="50%" alpha={0.25} size={1800} />
      )}
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 1. HOOK — "blurring faces shouldn't suck" (3s)
// ─────────────────────────────────────────────────────────────

const Hook: FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame;

  // Face circle pulse 0-15
  const facePulse = 1 + 0.08 * Math.sin(localFrame * 0.3);
  // Blur ramp on the face starts at frame 18
  const blurAmt = interpolate(localFrame, [18, 28], [0, 70], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // CENSOR bar slams in at frame 22
  const barIn = popIn(frame, 22, fps, {
    damping: 10,
    stiffness: 220,
    mass: 0.5,
  });
  const barScale = interpolate(barIn, [0, 1], [0, 1]);
  const barRot = interpolate(barIn, [0, 1], [-15, -8]);
  // Subhead appears at 40
  const sub = popIn(frame, 40, fps);

  return (
    <AbsoluteFill>
      <Bg variant="purple" />

      {/* "face" */}
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "center" }}
      >
        <div
          style={{
            width: 540,
            height: 700,
            borderRadius: 999,
            background: `radial-gradient(circle at 35% 35%, #ffdcb5 0%, ${COLORS.skin} 45%, #b07a55 100%)`,
            transform: `scale(${facePulse})`,
            filter: `blur(${blurAmt}px)`,
            boxShadow: "0 30px 90px rgba(0,0,0,0.5)",
          }}
        />
      </AbsoluteFill>

      {/* CENSOR bar */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `scale(${barScale}) rotate(${barRot}deg)`,
            background: "black",
            color: COLORS.text,
            padding: "26px 64px",
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 140,
            letterSpacing: 6,
            border: `8px solid ${COLORS.text}`,
            boxShadow: `0 0 80px ${COLORS.accent}`,
          }}
        >
          CENSORED
        </div>
      </AbsoluteFill>

      {/* Subhead */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 240,
        }}
      >
        <div
          style={{
            opacity: sub,
            transform: `translateY(${(1 - sub) * 40}px)`,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 800,
            fontSize: 96,
            textAlign: "center",
            lineHeight: 1.05,
            textShadow: "0 8px 30px rgba(0,0,0,0.6)",
          }}
        >
          blurring faces<br />shouldn't suck.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 2. PAIN — paid software pain points (5s)
// ─────────────────────────────────────────────────────────────

const PainItem: FC<{
  text: string;
  frame: number;
  start: number;
  end: number;
}> = ({ text, frame, start, end }) => {
  const a = fadeIn(frame, start, 6) * fadeOut(frame, end, 6);
  const slash = interpolate(frame, [start + 14, end - 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        opacity: a,
        position: "relative",
        color: COLORS.text,
        fontFamily: FONT_STACK,
        fontWeight: 900,
        fontSize: 130,
        textAlign: "center",
        padding: "0 60px",
        lineHeight: 1.0,
      }}
    >
      {text}
      <div
        style={{
          position: "absolute",
          left: "5%",
          top: "50%",
          width: `${slash * 90}%`,
          height: 18,
          background: COLORS.red,
          transform: "rotate(-6deg)",
          transformOrigin: "left",
          boxShadow: `0 0 30px ${COLORS.red}`,
        }}
      />
    </div>
  );
};

const Pain: FC = () => {
  const frame = useCurrentFrame();
  const items: { text: string; start: number; end: number }[] = [
    { text: "$50/mo subscriptions", start: 0, end: 35 },
    { text: "uploads to the cloud", start: 35, end: 75 },
    { text: "watermarks. duration limits.", start: 75, end: 120 },
    { text: "no thanks.", start: 120, end: 150 },
  ];
  return (
    <AbsoluteFill>
      <Bg variant="ink" />
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "center" }}
      >
        {items.map((it, i) => (
          <Sequence
            key={i}
            from={it.start}
            durationInFrames={it.end - it.start}
            layout="none"
          >
            <PainItem
              text={it.text}
              frame={frame}
              start={it.start}
              end={it.end}
            />
          </Sequence>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 3. REVEAL — brand drop (5s)
// ─────────────────────────────────────────────────────────────

const Reveal: FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame;

  const intro = popIn(frame, 0, fps, {
    damping: 14,
    stiffness: 140,
    mass: 0.5,
  });
  const logo = popIn(frame, 25, fps, {
    damping: 12,
    stiffness: 120,
    mass: 0.7,
  });
  const sub = fadeIn(frame, 55, 12);

  const scale = interpolate(logo, [0, 1], [0.6, 1]);
  const rot = interpolate(logo, [0, 1], [-8, 0]);

  return (
    <AbsoluteFill>
      <Bg variant="purple" />

      {/* "introducing" */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 380,
        }}
      >
        <div
          style={{
            opacity: intro * (1 - fadeIn(frame, 60, 10) * 0.7),
            color: COLORS.pink,
            fontFamily: FONT_STACK,
            fontWeight: 700,
            fontSize: 70,
            letterSpacing: 4,
            textTransform: "uppercase",
          }}
        >
          introducing
        </div>
      </AbsoluteFill>

      {/* big brand */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            transform: `scale(${scale}) rotate(${rot}deg)`,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 220,
            lineHeight: 0.95,
            textAlign: "center",
            textShadow: `0 0 60px ${COLORS.accent}`,
          }}
        >
          blur<br />faces.
        </div>
      </AbsoluteFill>

      {/* tagline */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 320,
        }}
      >
        <div
          style={{
            opacity: sub,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 700,
            fontSize: 72,
            textAlign: "center",
          }}
        >
          <span style={{ color: COLORS.accent }}>free.</span>{" "}
          <span style={{ color: COLORS.pink }}>local.</span>{" "}
          <span style={{ color: COLORS.green }}>no cap.</span>
        </div>
      </AbsoluteFill>

      {/* sparkle */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            width: 4,
            height: 4,
            borderRadius: 999,
            background: COLORS.text,
            boxShadow: `0 0 ${40 + 30 * Math.sin(local * 0.2)}px ${COLORS.accent}, 0 0 ${20 + 20 * Math.sin(local * 0.3)}px ${COLORS.pink}`,
            transform: `translateY(-260px) translateX(${260 * Math.sin(local * 0.05)}px)`,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 4. DEMO — show the app in action (17s)
// ─────────────────────────────────────────────────────────────

const FaceMini: FC<{ blur: number }> = ({ blur }) => (
  <div
    style={{
      width: 200,
      height: 240,
      borderRadius: 999,
      background: `radial-gradient(circle at 35% 35%, #ffdcb5 0%, ${COLORS.skin} 50%, #a06a45 100%)`,
      filter: `blur(${blur}px)`,
    }}
  />
);

const Demo: FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame;

  // window slides in 0-15
  const winIn = popIn(frame, 0, fps, {
    damping: 18,
    stiffness: 100,
    mass: 0.9,
  });

  // file flying in 50-80
  const fly = interpolate(local, [50, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fileVisible = local >= 50 && local <= 100;

  // processing 100-280
  const prog = interpolate(local, [100, 280], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const processing = local >= 95 && local <= 290;

  // result reveal at 300+
  const resultIn = popIn(frame, 300, fps, {
    damping: 12,
    stiffness: 130,
    mass: 0.6,
  });
  const showResult = local >= 295;

  // before/after split label
  const labelOpacity = interpolate(local, [320, 360], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Top label
  const headerY = interpolate(winIn, [0, 1], [-100, 0]);
  const winScale = interpolate(winIn, [0, 1], [0.85, 1]);
  const winOpacity = winIn;

  return (
    <AbsoluteFill>
      <Bg variant="ink" />

      {/* Header */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 100,
        }}
      >
        <div
          style={{
            transform: `translateY(${headerY}px)`,
            opacity: winOpacity,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 84,
            textAlign: "center",
            lineHeight: 1,
          }}
        >
          drag.{" "}
          <span style={{ color: COLORS.pink }}>drop.</span>{" "}
          <span style={{ color: COLORS.accent }}>done.</span>
        </div>
      </AbsoluteFill>

      {/* Mock app window */}
      <AbsoluteFill
        style={{ alignItems: "center", justifyContent: "center" }}
      >
        <div
          style={{
            transform: `scale(${winScale})`,
            opacity: winOpacity,
            width: 900,
            background: COLORS.card,
            border: `2px solid ${COLORS.accent}`,
            borderRadius: 22,
            boxShadow: `0 30px 80px rgba(0,0,0,0.5), 0 0 60px ${COLORS.accent}55`,
            overflow: "hidden",
          }}
        >
          {/* title bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              padding: "18px 22px",
              borderBottom: `1px solid ${COLORS.border}`,
              background: COLORS.bg,
            }}
          >
            <div style={{ width: 16, height: 16, borderRadius: 999, background: COLORS.red }} />
            <div style={{ width: 16, height: 16, borderRadius: 999, background: COLORS.yellow }} />
            <div style={{ width: 16, height: 16, borderRadius: 999, background: COLORS.green }} />
            <div
              style={{
                marginLeft: 18,
                color: COLORS.dim,
                fontFamily: FONT_STACK,
                fontSize: 26,
                fontWeight: 600,
              }}
            >
              blur faces — free, local, no cap
            </div>
          </div>

          {/* drop zone */}
          <div style={{ padding: 26 }}>
            <div
              style={{
                position: "relative",
                height: 320,
                borderRadius: 14,
                background: COLORS.card,
                border: `3px dashed ${COLORS.accent}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  color: COLORS.text,
                  fontFamily: FONT_STACK,
                  fontWeight: 800,
                  fontSize: 44,
                }}
              >
                drop ur vids here
              </div>

              {/* flying file */}
              {fileVisible && (
                <div
                  style={{
                    position: "absolute",
                    left: `${interpolate(fly, [0, 1], [-30, 50])}%`,
                    top: `${interpolate(fly, [0, 1], [-150, 35])}%`,
                    transform: `scale(${interpolate(fly, [0, 1], [1.4, 0.8])}) rotate(${interpolate(fly, [0, 1], [-20, 8])}deg)`,
                    opacity: interpolate(fly, [0.85, 1], [1, 0]),
                    width: 140,
                    height: 180,
                    background: COLORS.pink,
                    borderRadius: 14,
                    boxShadow: `0 20px 50px rgba(0,0,0,0.4), 0 0 40px ${COLORS.pink}99`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: COLORS.text,
                    fontFamily: FONT_STACK,
                    fontWeight: 900,
                    fontSize: 38,
                  }}
                >
                  MP4
                </div>
              )}
            </div>

            {/* progress */}
            {processing && (
              <div style={{ marginTop: 30 }}>
                <div
                  style={{
                    color: COLORS.accent,
                    fontFamily: MONO_STACK,
                    fontSize: 28,
                    marginBottom: 12,
                  }}
                >
                  cooking… {Math.round(prog)}%
                </div>
                <div
                  style={{
                    width: "100%",
                    height: 22,
                    background: COLORS.cardHi,
                    borderRadius: 999,
                    overflow: "hidden",
                    border: `1px solid ${COLORS.border}`,
                  }}
                >
                  <div
                    style={{
                      width: `${prog}%`,
                      height: "100%",
                      background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.pink})`,
                      boxShadow: `0 0 25px ${COLORS.accent}`,
                    }}
                  />
                </div>
              </div>
            )}

            {/* result row */}
            {showResult && (
              <div
                style={{
                  marginTop: 30,
                  display: "flex",
                  gap: 40,
                  alignItems: "center",
                  justifyContent: "center",
                  transform: `scale(${interpolate(resultIn, [0, 1], [0.6, 1])})`,
                  opacity: resultIn,
                }}
              >
                <div style={{ textAlign: "center" }}>
                  <FaceMini blur={0} />
                  <div
                    style={{
                      marginTop: 14,
                      color: COLORS.dim,
                      fontFamily: FONT_STACK,
                      fontWeight: 700,
                      fontSize: 28,
                      opacity: labelOpacity,
                    }}
                  >
                    before
                  </div>
                </div>
                <div
                  style={{
                    color: COLORS.accent,
                    fontFamily: FONT_STACK,
                    fontWeight: 900,
                    fontSize: 80,
                  }}
                >
                  →
                </div>
                <div style={{ textAlign: "center" }}>
                  <FaceMini blur={32} />
                  <div
                    style={{
                      marginTop: 14,
                      color: COLORS.green,
                      fontFamily: FONT_STACK,
                      fontWeight: 700,
                      fontSize: 28,
                      opacity: labelOpacity,
                    }}
                  >
                    after ✨
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>

      {/* Bottom call-out */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 180,
        }}
      >
        <div
          style={{
            opacity: fadeIn(frame, 380, 14),
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 800,
            fontSize: 56,
            textAlign: "center",
            background: COLORS.card,
            border: `2px solid ${COLORS.pink}`,
            padding: "16px 36px",
            borderRadius: 999,
          }}
        >
          100% on your device. zero upload.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 5. FEATURES — six benefit cards (12s)
// ─────────────────────────────────────────────────────────────

const FeatureCard: FC<{
  icon: string;
  title: string;
  sub: string;
  start: number;
  color: string;
}> = ({ icon, title, sub, start, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = popIn(frame, start, fps, {
    damping: 14,
    stiffness: 130,
    mass: 0.6,
  });
  return (
    <div
      style={{
        transform: `scale(${interpolate(s, [0, 1], [0.4, 1])}) translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
        opacity: s,
        flex: "0 0 calc(50% - 16px)",
        background: COLORS.card,
        border: `2px solid ${color}`,
        borderRadius: 26,
        padding: 30,
        boxShadow: `0 14px 40px rgba(0,0,0,0.4), 0 0 50px ${color}33`,
      }}
    >
      <div style={{ fontSize: 86, lineHeight: 1, marginBottom: 14 }}>{icon}</div>
      <div
        style={{
          color: COLORS.text,
          fontFamily: FONT_STACK,
          fontWeight: 900,
          fontSize: 50,
          lineHeight: 1.05,
        }}
      >
        {title}
      </div>
      <div
        style={{
          color: COLORS.dim,
          fontFamily: FONT_STACK,
          fontWeight: 600,
          fontSize: 30,
          marginTop: 8,
        }}
      >
        {sub}
      </div>
    </div>
  );
};

const Features: FC = () => {
  const frame = useCurrentFrame();
  const headerS = popIn(frame, 0, 30);

  const cards: { icon: string; title: string; sub: string; color: string }[] = [
    { icon: "🔒", title: "100% local", sub: "no upload, ever", color: COLORS.accent },
    { icon: "⚡", title: "GPU fast", sub: "DirectML + Neural Engine", color: COLORS.pink },
    { icon: "🎬", title: "batch mode", sub: "drop 50 vids at once", color: COLORS.green },
    { icon: "🍎", title: "Win + Mac", sub: "Apple Silicon ready", color: COLORS.yellow },
    { icon: "💸", title: "free forever", sub: "MIT, no watermark", color: COLORS.accentHot },
    { icon: "✨", title: "drag & drop", sub: "literally that's it", color: COLORS.pinkHot },
  ];

  return (
    <AbsoluteFill>
      <Bg variant="purple" />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 140,
        }}
      >
        <div
          style={{
            transform: `scale(${interpolate(headerS, [0, 1], [0.7, 1])})`,
            opacity: headerS,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 110,
            textAlign: "center",
            lineHeight: 0.95,
          }}
        >
          built<br />different.
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 140,
        }}
      >
        <div
          style={{
            width: 920,
            display: "flex",
            flexWrap: "wrap",
            gap: 32,
            justifyContent: "center",
          }}
        >
          {cards.map((c, i) => (
            <FeatureCard
              key={i}
              icon={c.icon}
              title={c.title}
              sub={c.sub}
              color={c.color}
              start={30 + i * 18}
            />
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 6. INSTALL — 3 steps (8s)
// ─────────────────────────────────────────────────────────────

const Step: FC<{
  n: number;
  title: string;
  desc: string;
  start: number;
}> = ({ n, title, desc, start }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = popIn(frame, start, fps, {
    damping: 13,
    stiffness: 140,
    mass: 0.6,
  });
  return (
    <div
      style={{
        transform: `translateX(${interpolate(s, [0, 1], [-60, 0])}px)`,
        opacity: s,
        display: "flex",
        alignItems: "center",
        gap: 32,
        background: COLORS.card,
        border: `2px solid ${COLORS.accent}55`,
        borderRadius: 28,
        padding: 26,
        width: 880,
      }}
    >
      <div
        style={{
          width: 110,
          height: 110,
          borderRadius: 26,
          background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.pink})`,
          color: COLORS.bg,
          fontFamily: FONT_STACK,
          fontWeight: 900,
          fontSize: 78,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: `0 0 30px ${COLORS.accent}aa`,
        }}
      >
        {n}
      </div>
      <div style={{ flex: 1 }}>
        <div
          style={{
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 54,
            lineHeight: 1.05,
          }}
        >
          {title}
        </div>
        <div
          style={{
            color: COLORS.dim,
            fontFamily: FONT_STACK,
            fontSize: 30,
            marginTop: 6,
          }}
        >
          {desc}
        </div>
      </div>
    </div>
  );
};

const Install: FC = () => {
  const frame = useCurrentFrame();
  const headerS = popIn(frame, 0, 30);
  return (
    <AbsoluteFill>
      <Bg variant="ink" />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 220,
        }}
      >
        <div
          style={{
            transform: `scale(${interpolate(headerS, [0, 1], [0.7, 1])})`,
            opacity: headerS,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 110,
            textAlign: "center",
            lineHeight: 0.95,
          }}
        >
          install in<br />60 seconds.
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          paddingTop: 200,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          <Step
            n={1}
            title="install python"
            desc="python.org → tick 'add to PATH'"
            start={25}
          />
          <Step
            n={2}
            title="double-click install"
            desc="install.bat (Win) or install.command (Mac)"
            start={60}
          />
          <Step
            n={3}
            title="drag a vid in"
            desc="that's it. faces blurred."
            start={95}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// 7. CTA — github + freefaceblur.com (10s)
// ─────────────────────────────────────────────────────────────

const CTA: FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame;

  const titleS = popIn(frame, 0, fps, {
    damping: 12,
    stiffness: 130,
    mass: 0.6,
  });
  const githubS = popIn(frame, 25, fps);
  const proS = popIn(frame, 90, fps);
  const finS = fadeIn(frame, 180, 18);

  const pulse = 1 + 0.04 * Math.sin(local * 0.25);

  return (
    <AbsoluteFill>
      <Bg variant="pink" />

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: 240,
        }}
      >
        <div
          style={{
            transform: `scale(${interpolate(titleS, [0, 1], [0.6, 1])})`,
            opacity: titleS,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 900,
            fontSize: 170,
            textAlign: "center",
            lineHeight: 0.92,
            textShadow: `0 0 60px ${COLORS.accent}`,
          }}
        >
          get it.<br />it's free.
        </div>
      </AbsoluteFill>

      {/* Github */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          paddingTop: 100,
        }}
      >
        <div
          style={{
            transform: `scale(${interpolate(githubS, [0, 1], [0.8, 1]) * pulse})`,
            opacity: githubS,
            background: COLORS.card,
            border: `4px solid ${COLORS.accent}`,
            borderRadius: 30,
            padding: "30px 56px",
            color: COLORS.text,
            fontFamily: MONO_STACK,
            fontWeight: 900,
            fontSize: 52,
            textAlign: "center",
            boxShadow: `0 0 80px ${COLORS.accent}99`,
          }}
        >
          github.com/Teylersf/<br />blurfacefree
        </div>
      </AbsoluteFill>

      {/* Pro */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 340,
        }}
      >
        <div
          style={{
            opacity: proS,
            transform: `translateY(${interpolate(proS, [0, 1], [40, 0])}px)`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              color: COLORS.dim,
              fontFamily: FONT_STACK,
              fontWeight: 700,
              fontSize: 36,
              marginBottom: 10,
            }}
          >
            need cloud + commercial?
          </div>
          <div
            style={{
              color: COLORS.pink,
              fontFamily: FONT_STACK,
              fontWeight: 900,
              fontSize: 68,
              textShadow: `0 0 40px ${COLORS.pink}`,
            }}
          >
            freefaceblur.com
          </div>
        </div>
      </AbsoluteFill>

      {/* Final stamp */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: 180,
        }}
      >
        <div
          style={{
            opacity: finS,
            color: COLORS.text,
            fontFamily: FONT_STACK,
            fontWeight: 800,
            fontSize: 44,
            background: COLORS.bg,
            padding: "12px 28px",
            borderRadius: 999,
            border: `2px solid ${COLORS.text}`,
          }}
        >
          ✨ blur faces — free forever ✨
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─────────────────────────────────────────────────────────────
// Root composition
// ─────────────────────────────────────────────────────────────

export const Promo: FC = () => {
  return (
    <AbsoluteFill style={{ background: COLORS.bg, overflow: "hidden" }}>
      <Sequence from={T_HOOK} durationInFrames={T_PAIN - T_HOOK}>
        <Hook />
      </Sequence>
      <Sequence from={T_PAIN} durationInFrames={T_REVEAL - T_PAIN}>
        <Pain />
      </Sequence>
      <Sequence from={T_REVEAL} durationInFrames={T_DEMO - T_REVEAL}>
        <Reveal />
      </Sequence>
      <Sequence from={T_DEMO} durationInFrames={T_FEATS - T_DEMO}>
        <Demo />
      </Sequence>
      <Sequence from={T_FEATS} durationInFrames={T_INSTALL - T_FEATS}>
        <Features />
      </Sequence>
      <Sequence from={T_INSTALL} durationInFrames={T_CTA - T_INSTALL}>
        <Install />
      </Sequence>
      <Sequence from={T_CTA} durationInFrames={DURATION - T_CTA}>
        <CTA />
      </Sequence>
    </AbsoluteFill>
  );
};
