"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";

import Particles from "@/components/ui/particles";

import { cn } from "@/lib/utils";
import AnimatedShinyText from "@/components/ui/animated-shiny-text";
import WordPullUp from "@/components/ui/word-pull-up";

import BlurIn from "@/components/ui/blur-in";
import ShimmerButton from "@/components/ui/shimmer-button";
import BlurFade from "@/components/ui/blur-fade";
import IconCloud from "@/components/ui/icon-cloud";
import { ArrowRightIcon } from "@radix-ui/react-icons";

import HeroVideoDialog from "@/components/ui/hero-video-dialog";
import { FaChartLine, FaCalendarAlt, FaSyncAlt } from "react-icons/fa";

import { RainbowButton } from "@/components/ui/rainbow-button";

import { BorderBeam } from "@/components/ui/border-beam";

export default function Home() {
  const images = Array.from({ length: 5 }, (_, i) => {
    const isLandscape = i % 2 === 0;
    const width = isLandscape ? 800 : 600;
    const height = isLandscape ? 600 : 800;
    return `/images/farcry${i + 1}.png`;
  });

  const slugs = [
    "typescript",
    "javascript",
    "react",
    "html5",
    "css3",
    "nextdotjs",
    "supabase",
    "vercel",
    "docker",
    "git",
    "github",
    "visualstudiocode",
    "fastapi",
    "streamlit",
    "python",
  ];

  const { theme } = useTheme();
  const [color, setColor] = useState("#ffffff");

  useEffect(() => {
    setColor(theme === "dark" ? "#ffffff" : "#000000");
  }, [theme]);

  return (
    <div>
      <div className="relative flex h-[400px] w-full flex-col items-center justify-center overflow-hidden rounded-lg bg-background">
        <Particles
          className="absolute inset-0"
          quantity={400}
          ease={60}
          color={color}
          refresh
        />

        <div className="z-10 flex min-h-48 items-center justify-center">
          <a
            href="https://github.com/josevalencar/Farcry"
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "group rounded-full border border-black/5 bg-neutral-100 text-base text-white transition-all ease-in hover:cursor-pointer hover:bg-neutral-200 dark:border-white/5 dark:bg-neutral-900 dark:hover:bg-neutral-800"
            )}
          >
            <AnimatedShinyText className="inline-flex items-center justify-center px-3 py-1 text-sm transition ease-out hover:text-neutral-600 hover:duration-300 hover:dark:text-neutral-400">
              <span className="text-md">🪙 Introducing Farcry</span>
              <ArrowRightIcon className="ml-2 size-3 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5" />
            </AnimatedShinyText>
          </a>
        </div>

        <div>
          <WordPullUp
            className="text-lg font-medium tracking-[-0.02em] text-black dark:text-white md:text-4xl md:leading-[3rem]"
            words="Forecast Your Crypto With AI"
          />
        </div>

        <div className="mt-1">  {/* Reduce top margin to bring elements closer */}
          <BlurIn
            word="The all-in-one cryptocurrency forecasting tool."
            className="text-xs font-normal text-gray-500 dark:text-gray-300"
            duration={3}
          />
        </div>
      </div>

      <div className="z-10 flex min-h-48 items-center justify-center mt-2">
        <BlurFade delay={2.0} inView>
          <a
        href="https://inteli.gitbook.io/farcry-cryptocurrency-forecasting-tool"
        target="_blank"
        rel="noopener noreferrer"
          >
        <ShimmerButton className="shadow-lg px-3 py-1.5">
          <span className="whitespace-pre-wrap text-center text-sm font-medium leading-none tracking-tight text-white dark:from-white dark:to-slate-900/10 lg:text-base">
            See Full Documentation
          </span>
        </ShimmerButton>
          </a>
        </BlurFade>
      </div>

      <div className="relative w-3/4 mx-auto pb-24">
        <div className="relative flex h-[500px] w-full flex-col items-center justify-center overflow-hidden rounded-lg border bg-background md:shadow-xl mb-8">
          <HeroVideoDialog
            className="dark:hidden block"
            animationStyle="from-center"
            videoSrc="https://www.youtube.com/embed/8FLRGvzn_EE"
            thumbnailSrc="/images/farcry1.png"
            thumbnailAlt="Hero Video"
          />
          <BorderBeam size={500} duration={12} delay={9} colorFrom="#000000" colorTo="#0000ff" />
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-16 px-6 sm:px-8 lg:px-10 pb-32">
        <BlurFade delay={0.45} inView>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 p-4 rounded-full">
                <FaChartLine className="h-12 w-12 text-black-500" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                Accurate Crypto Forecasts
              </h3>
              <p className="mt-3 text-base text-gray-600">
                Farcry provides accurate forecasts of Bitcoin (BTC) and Ethereum
                (ETH) closing prices, offering valuable insights for traders and
                investors.
              </p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 p-4 rounded-full">
                <FaCalendarAlt className="h-12 w-12 text-black-500" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                90-Day Forecasts
              </h3>
              <p className="mt-3 text-base text-gray-600">
                Farcry leverages Time Series and Machine Learning regression
                models to generate 90-day forecasts, helping users plan for the
                future with confidence.
              </p>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="bg-blue-100 p-4 rounded-full">
                <FaSyncAlt className="h-12 w-12 text-black-500" />
              </div>
              <h3 className="mt-6 text-xl font-semibold text-gray-900">
                Real-Time Data Updates
              </h3>
              <p className="mt-3 text-base text-gray-600">
                Using continuously updated market data, Farcry ensures that
                users have the latest insights for making informed cryptocurrency
                investment decisions.
              </p>
            </div>
          </div>
        </BlurFade>
      </div>

      <section id="photos">
        <div className="columns-2 gap-4 sm:columns-3">
          {images.map((imageUrl, idx) => (
            <BlurFade key={imageUrl} delay={0.25 + idx * 0.05} inView>
              <img
                className="mb-4 size-full rounded-lg object-contain"
                src={imageUrl}
                alt={`Random stock image ${idx + 1}`}
              />
            </BlurFade>
          ))}
        </div>
      </section>

      <section id="header" className="flex flex-col items-center pt-24">
        <BlurFade delay={0.25} inView>
          <h2 className="text-2xl font-bold tracking-tighter sm:text-4xl xl:text-5xl/none">
            Stack 🥞
          </h2>
        </BlurFade>
        <BlurFade delay={0.25 * 2} inView>
          <span className="text-lg text-pretty tracking-tighter sm:text-2xl xl:text-3xl/none text-center">
            Our stack includes cutting-edge technologies to ensure the best
            performance and scalability.
          </span>
        </BlurFade>
      </section>

      <div className="relative flex w-full max-w-2xl items-center justify-center overflow-hidden rounded-lg bg-background px-16 pb-2 pt-6 mx-auto my-8">
        <IconCloud iconSlugs={slugs} />
      </div>
      <div className="z-10 flex min-h-48 items-center justify-center h-80 w-full">
        <a
          href="https://github.com/josevalencar/Farcry"
          target="_blank"
          rel="noopener noreferrer"
        >
          <RainbowButton>Access GitHub</RainbowButton>
        </a>
      </div>
    </div>
  );
}
