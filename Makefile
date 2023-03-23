VERSION = v0.2.4-alpha

make all: app dmg

app:
	python3.9 setup.py py2app

alias:
	python3.9 setup.py py2app -A

run:
	./dist/Tomado.app/Contents/MacOS/Tomado

dmg:
	create-dmg \
	--volname "Tomado Installer $(VERSION)" \
	--volicon "/Users/danielgalis/Desktop/code/Tomado/icons/tomado.icns" \
	--window-pos 100 60 \
	--window-size 430 270 \
	--icon-size 100 \
	--icon "Tomado.app" 100 100 \
	--hide-extension "Tomado.app" \
	--app-drop-link 300 100 \
	"Tomado-Installer-$(VERSION).dmg" \
	"/Users/danielgalis/Desktop/code/Tomado/dist"

.PHONY: clean

clean:
	rm -rf build dist
	rm -rf *.dmg