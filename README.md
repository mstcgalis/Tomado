# Tomado 🍅

Simple Pomodoro Timer that lives in your MacOS menu bar 💻

<img width="222" alt="screenshot of the app" src="https://user-images.githubusercontent.com/77400726/169261760-777aa046-c670-432d-8a31-c3e76d2590ed.png">

Please create a Pull Request or Issue if you encounter an error. I'm also always open to talk 🌱

# Installation

1. Download `Tomado-Installer.dmg` from the latest [release](https://github.com/mstcgalis/Tomado/releases/tag/v0.2.4-alpha) (v0.2.3-alpha)
2. Mount the `.dmg` and move `🍅 Tomado` to `Applications`
3. Open `🍅 Tomado`
4. Go to `System Preferences -> Security & Privacy -> General -> click "Open Anyway"`
5. Thenks for installing! 😊 Don't forget to **🔔 Enable notifications** ↓

## 🔔 Enable notifications

1. Go to `System Preferences -> Notifications & Focus -> Notifications`
2. Find Tomado in the side panel
3. Toggle `Allow Notifications` and select your prefered style
4. You're done! 🌸 

# Building from source code

1. Clone the repository: `$ git clone https://github.com/mstcgalis/Tomado.git`
- (recommended) Create adn activate a virtual python enviroment.
2. Make sure to install all the dependencies using `$ pip install -r requirements.txt`

3. Use the Makefile:
  - `$ make clean` cleans every built file
  - `$ make alias` builds the app in alias mode (dev, not standalone - no need to build repeatedly again when editing source code)
  - `$ make app` builds the standalone app at -> `Tomado/dist/Tomado.app`
  - `$ make dmg` created the installer dmg at -> `Tomado/Tomado-version-installer.dmg
  - `$ make all` = `$ make app` + `$ make dmg`

4. Launching and using the app:
  - Go to `System Preferences -> Security & Privacy -> General -> click "Open Anyway"`
  - (optional) **🔔 Enable notifications**

---

made with ❤️, care and patience by [Daniel Gális](https://www.are.na/daniel-galis)

part of [self.governance(software)](https://www.are.na/daniel-galis/self-governance)
