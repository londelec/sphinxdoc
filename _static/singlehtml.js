/*jslint vars: true */
/*global $ */

$(function () {
	'use strict';

	function parseSubTree(header) {
		var topAnchor = header.attr('href');
		var subTree = header.next();
        
		if (subTree.length) {
			subTree.find('>li>a').each(function () {
				var self = $(this);
				var anchor = self.attr('href');
				var fullAnchor = topAnchor + '-' + anchor.substr(1);
				self.attr('href', fullAnchor);
				var label = $(document.getElementById(anchor.substr(1)));
                if (label.length) {
                    label.attr('id', fullAnchor.substr(1));
                }
				parseSubTree(self);
			});
		}
	}

	function fixTreeview() {
		/* This API has been removed in jQuery 3.0; use .addBack() instead, which should work identically. */
		if (toctree.andSelf)
			toctree.find('ul').andSelf().addClass('nav');
		else if (toctree.addBack)
			toctree.find('ul').addBack().addClass('nav');
		else
			console.log("Error: jQuery doesn't have andSelf() nor addBack() methods")
	    toctree.find('a').each(function () {
	        var self = $(this);
	        var anchor = this.href.substr(this.href.indexOf("#"));
	        this.href = anchor;
	        
	        if (self.next().hasClass('nav')) {
	            self.prepend(caretTemplate);
	        }
	    });

	    toctree.find('.toctree-l1 > a').each(function () {
	        var self = $(this);
	        var anchor = self.attr('href');
	        var fixedAnchor = anchor.replace('/', '-');
	        var label = $(document.getElementById(anchor.substr(1)));
	        if (label.length) {
	            var section = label.next();
	            if (section.hasClass('section')) {
	                label.remove();
	                self.attr('href', fixedAnchor);
	                section.attr('id', fixedAnchor.substr(1));
	                parseSubTree(self);
	            }
	        }
	    });		
	}	

	$('.document').attr('id', 'document-index');
	$('h1').addClass('page-header');

    var doc = $(document);
	var body = $(document.body);
    var sidebar = body.find('.sphinxsidebar');
    var toctree = sidebar.find('.sphinxsidebarwrapper>ul');
    var caretTemplate = '<span class="caret-wrap"><span class="caret"></span></span>';

    sidebar.wrap('<div class="sidebar-container">');
    sidebar.before('<div id="dragbar"></div>');

    var mainContent = $('.bodywrapper');
    var sidebarContainer = $('.sidebar-container');
    var dragbarWidth = $('#dragbar').outerWidth();
    var newWidth = 0;

    sidebarContainer.css({'width': 0});
    mainContent.css({'margin-left': 0});

    setTimeout(function() {
    	fixTreeview();
        sidebarContainer.animate({'width': 320}, 400, "linear", function() {
        	mainContent.css({'margin-left': 320});
        	body.scrollspy("refresh");
        	
        	if(window.location.hash) {
        		var tmpHash = window.location.hash;
        		window.location.hash = '';
        		window.location.hash = tmpHash;
        	}
        	else {
        		body.scrollspy("process");
        	}
        });
    }, 0);

    toctree.on('click', 'a .caret-wrap', function (e) {
        e.stopPropagation();
        var list = $(this).closest('li');
        
        if (list.length) {
            if (list.hasClass('active')) {
                list.removeClass('active').removeClass('expanded');
            } else {
                list.toggleClass('expanded');
            }
        }
         
        return false;
    });

    body.on('activate.bs.scrollspy', function (e) {
        var self = $(e.target);
        if (self.hasClass('active')) {
            self.addClass('expanded');

            var sidebarHeight = sidebar.height();
            var sidebarScroll = sidebar.scrollTop();
            var sidebarBottom = sidebarHeight + sidebarScroll;

            var link = self.children(":first");
            var linkHeight = link.outerHeight();
            var linkTop = link.offset().top - sidebar.offset().top + sidebarScroll;
            var linkBottom = linkTop + linkHeight;

            if (linkBottom > sidebarBottom) {
                sidebar.scrollTop(linkBottom - sidebarHeight);
            } else if (linkTop < sidebarScroll) {
                sidebar.scrollTop(linkTop);
            }
        }
    });

    body.scrollspy({ target: ".sphinxsidebarwrapper", offset: 200 });

    doc.on('mousedown', '#dragbar', function (e) {
        e.preventDefault();

        var maxWidth = body.innerWidth();
        var updateTimer = null;
        doc.on('mousemove', function (e) {
            clearTimeout(updateTimer);
            newWidth = e.pageX;
            if (newWidth > maxWidth) {
                newWidth = maxWidth;
            }

            if (newWidth < dragbarWidth) {
                newWidth = dragbarWidth;
            }

            sidebarContainer.css("width", newWidth);
            updateTimer = setTimeout(function () {
                mainContent.css("margin-left", newWidth);
            }, 20);
        });
    }).on('mouseup', function (e) {
        doc.off('mousemove');
    });
});
