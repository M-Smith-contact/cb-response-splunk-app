APPNAME=DA-ESS-CbResponse
VERSION=1.0.0
BUNDLE=$(APPNAME)-$(VERSION)
all: $(APPNAME).spl

clean:
	rm -f build/$(APPNAME).spl
	rm -rf build/$(APPNAME)

test: $(APPNAME).spl
	curl -X POST -H "Authorization: bearer $(SPLUNK_TOKEN)" -H "Cache-Control: no-cache" -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" -F "app_package=@build/$(APPNAME).spl" https://appinspect.splunk.com/v1/app/validate

$(APPNAME).spl: clean
	mkdir -p build/$(APPNAME)

	cp -r $(APPNAME)/appserver build/$(APPNAME)
	cp -r $(APPNAME)/bin build/$(APPNAME)
	cp -r $(APPNAME)/default build/$(APPNAME)
	cp -r $(APPNAME)/metadata build/$(APPNAME)
	cp -r $(APPNAME)/static build/$(APPNAME)
	cp -r $(APPNAME)/README build/$(APPNAME)
	cp LICENSE.md build/$(APPNAME)
	cp README.md build/$(APPNAME)

	find build/$(APPNAME) -name ".*" -delete
	find build/$(APPNAME) -name "*.pyc" -delete

	(cd build && COPYFILE_DISABLE=1 tar -cvzf $(APPNAME).spl $(APPNAME))
