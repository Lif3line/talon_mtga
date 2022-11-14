# MTGA Talon

Talon integration for Magic: The Gathering Arena (MTGA). Uses screen-based recognition to play cards and press buttons. Still requires some manual input for cards with targets and selecting blockers/attackers, but gets 80% of the way.

Caveats:

- Tuned on a 1440p screen, may need tweaking for other resolutions
- Has some edge cases with unusual card boards
- Can struggle if you have many cards in hand
- Still needs other interaction tools for blocks, individual attackers, and some uncommon interactions

## Setup

- Clone repo to Talon user folder e.g. `C:\Users\<username>\AppData\Roaming\talon`
- Install [Anaconda 3](https://www.anaconda.com/)
  - Assume default installation path
- Create environment from provided yaml `conda env create -f talon_env.yaml`
  - Assume name `talon`
  - This is used to load tools without messing with the Talon virtual environment
    - This step can be substituted to installing the packages in [talon_env.yaml](talon_env.yaml) into your Talon environment
- Reload Talon

## Usage

- Run MTGA in full-screen
  - Disable alternate card arts
  - Ensure there are no overlays in the way
- Activate the MTGA mode by saying `enable magic mode`
  - Ensures we don't clash with other commands
- Use `highlight cards` or `keep highlighting cards` to show overlays and ensure that you're playing the thing you want
  - Highlights will close automatically or in continuous mode stopped with `stop highlighting cards`
  - Use `select card X` to activate a card
  - Use `play X` to play a card
  - You can skip highlighting first by saying `fast X`
- Use `done` or `ok` to press any orange button
- See [mtga.talon](mtga.talon) for full command list
- **Note:** Provides the `mouse` talon integration for `mtga` mode from the excellent [knausj_talon](https://github.com/knausj85/knausj_talon)

## Example Overlay

![MTGA with Talon Overlay](img/mtga_screenshot_talon.png)

## Notes

Fairly hacky approach to the optical recognition of the cards, but it runs decently fast and works most of the time.

- Aims to run fast (currently <0.1s locally)
  - Lets numpy/OpenCV do the majority of the heavy lifting
- Use MTGA's blue/yellow "playable" border to find the rough region
  - Left-most card has a darkened effect
  - Use region to strip out everything else
- Use black border to find individual cards
  - Will always be delineated by blue borders
  - Parametrise black border to catch most cases
  - Pull border coordinates to get a clickable position
