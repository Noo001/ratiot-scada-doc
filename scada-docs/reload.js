$(document).ready(function() {

	var hash = window.location.hash.substr(1);
	var href = $('#nav li a').each(function(){
		var href = $(this).attr('href');
		if(hash==href.substr(0,href.length-5)){
			var toLoad = hash+'.html #content';
			$('#content').load(toLoad)
		}
	});

	$('#nav li a').on('click', function(e) {
		e.preventDefault();

		const nav = document.querySelector("#nav");

		// Remove all "active" styles from all elements in the nav
		Array.from(nav.querySelectorAll('.current, .current-page')).forEach(
			(el) => {
				el.classList.remove('current', 'current-page')
				el.classList.add('normal')
			}
		);

		// Collect all parents
		let parentNode = this.parentNode;
		var parents = [];
		while (parentNode) {
			parents.unshift(parentNode);
			parentNode = parentNode.parentNode;
		}

		// Filter parents to add "active" styles
		const filteredParents = parents.filter(el => {
			return el?.matches?.("[class*='toctree-']")
		})

		filteredParents.forEach(
			(el) => {
				el.classList.remove('normal')
				el.classList.add('current', 'current-page')
			}
		);
	});

	$('#nav li a').click(function() {
		var toLoad = $(this).attr('href') + ' #content';
		var hyperT = $(this).text();
		var targetHref = $(this).attr('href');
		var $content = $('#content');

		$('#load').remove();
		$('.article-container').append('<span id="load"><!-- LOADING... --></span>');
		$('#load').fadeIn('normal');

		$content.fadeOut(150, function() {

			$content.parent().load(toLoad, function(response, status, xhr) {
				
				// If AJAX fails (e.g., CORS/Security restriction on file://)
				if (status === "error") {
					// Standard page navigation for local files
					window.location.href = targetHref;
					return;
				}

				document.title = hyperT;
				
				try {
					window.history.pushState(
						{id: 'home', source: 'web'}, 
						hyperT, 
						targetHref
					);
				} catch (err) {
					// Ignore pushState errors (common in file:// protocol)
				}

				$content.fadeIn(150, function() {
					$('#load').fadeOut('normal');
				});
			});
		});
		return false;
	});

});