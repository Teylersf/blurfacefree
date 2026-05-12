import { Composition } from "remotion";
import { Promo, FPS, DURATION } from "./Promo";

export const Root = () => (
  <>
    <Composition
      id="Promo"
      component={Promo}
      durationInFrames={DURATION}
      fps={FPS}
      width={1080}
      height={1920}
    />
  </>
);
