# MTGA Talon

Talon integration for Magic: The Gathering Arena (MTGA). Uses screen-based recognition to play cards and press buttons. Still requires some manual input for cards with targets and selecting blockers/attackers, but gets a good chunk of the way.

Caveats:

- Tuned on a 1440p screen, may need tweaking for other resolutions
- Has some edge cases with unusual card borders
- Can struggle if you have many cards in hand
- Still needs other interaction tools for blocks, individual attackers, and generally uncommon interactions
  - Pairs nicely with an eye-tracker for this

Short video of usage: <https://youtu.be/hkBFbhc1mvg>

## Setup

- Clone repo to Talon user folder e.g. `C:\Users\<username>\AppData\Roaming\talon`
- Either install dependencies manually or install [Anaconda 3](https://www.anaconda.com/)
  - **Manually**
    - Open `C:\Users\<username>\AppData\Roaming\talon\.venv\Scripts` in command prompt
    - `pip install "numpy>=1.21.4" "opencv-contrib-python==4.5.5.62" "opencv-python-headless==4.5.5.62" "pillow>=8.4.0" pyautogui`
  - **Anaconda 3**
    - Create environment from provided yaml `conda env create -f talon_env.yaml`
      - This is allows side-loading tools without messing with the Talon virtual environment
- Reload Talon

## Usage

- Consider turning off subtitles as unfortunately they appear over the cards and can't easily be moved
- Run MTGA in full-screen
  - Disable alternate card arts
  - Ensure there are no overlays in the way
- A special magic mode will be enable when selecting MTGA which disables other commands to improve detection
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
