VERSION = v0.2.1-alpha

make all: app dmg

app:
	python setup.py py2app

dmg:
	create-dmg \
	--volname "Tomado Installer $(VERSION)" \
	--volicon "/Users/admin/Desktop/tomado/Tomado/icons/tomado.icns" \
	--window-pos 100 60 \
	--window-size 430 270 \
	--icon-size 100 \
	--icon "Tomado.app" 100 100 \
	--hide-extension "Tomado.app" \
	--app-drop-link 300 100 \
	"Tomado-Installer-$(VERSION).dmg" \
	"/Users/admin/Desktop/tomado/Tomado/Tomado/dist"

.PHONY: clean

clean:
	rm -rf build dist
	rm -rf *.dmg