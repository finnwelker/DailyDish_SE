console.log('DailyDish app loaded');

(function attachPdfDownloader() {
	function splitCommaList(text) {
		return String(text || '')
			.split(',')
			.map(item => item.trim())
			.filter(Boolean);
	}

	function splitInstructionSteps(text) {
		return String(text || '')
			.split(/(?=\d+\.)/)
			.map(step => step.trim())
			.filter(Boolean);
	}

	function sanitizeFileName(title) {
		const cleaned = String(title || 'rezept')
			.toLowerCase()
			.replace(/[^a-z0-9\s-_]/g, '')
			.replace(/\s+/g, '-')
			.replace(/-+/g, '-')
			.replace(/^[-_]+|[-_]+$/g, '');
		return cleaned || 'rezept';
	}

	function normalizeRecipe(recipe) {
		const tags = Array.isArray(recipe.tags)
			? recipe.tags.map(tag => (typeof tag === 'string' ? tag : tag && tag.name)).filter(Boolean)
			: splitCommaList(recipe.tags);

		const ingredients = Array.isArray(recipe.ingredients)
			? recipe.ingredients.map(item => String(item).trim()).filter(Boolean)
			: splitCommaList(recipe.ingredients);

		const instructions = splitInstructionSteps(recipe.instructions);

		return {
			title: String(recipe.title || '').trim(),
			description: String(recipe.description || '').trim(),
			tags,
			ingredients,
			instructions
		};
	}

	function ensureJsPdf() {
		return window.jspdf && window.jspdf.jsPDF;
	}

	window.downloadRecipeAsPdf = function downloadRecipeAsPdf(recipe) {
		if (!recipe) return;

		const JsPdfConstructor = ensureJsPdf();
		if (!JsPdfConstructor) {
			console.error('jsPDF konnte nicht geladen werden.');
			return;
		}

		const normalized = normalizeRecipe(recipe);
		const doc = new JsPdfConstructor({ unit: 'pt', format: 'a4' });
		const pageHeight = doc.internal.pageSize.getHeight();
		const left = 48;
		const right = 48;
		const contentWidth = doc.internal.pageSize.getWidth() - left - right;
		const lineHeight = 16;
		let y = 58;

		function ensureSpace(requiredHeight) {
			if (y + requiredHeight > pageHeight - 48) {
				doc.addPage();
				y = 58;
			}
		}

		function writeParagraph(text, fontSize, spacingAfter) {
			if (!text) return;
			doc.setFont('helvetica', 'normal');
			doc.setFontSize(fontSize);
			const lines = doc.splitTextToSize(text, contentWidth);
			ensureSpace(lines.length * lineHeight + spacingAfter);
			doc.text(lines, left, y);
			y += lines.length * lineHeight + spacingAfter;
		}

		function writeHeading(text) {
			doc.setFont('helvetica', 'bold');
			doc.setFontSize(14);
			ensureSpace(24);
			doc.text(text, left, y);
			y += 20;
		}

		doc.setFont('helvetica', 'bold');
		doc.setFontSize(22);
		const title = normalized.title || 'Rezept';
		const titleLines = doc.splitTextToSize(title, contentWidth);
		ensureSpace(titleLines.length * 24 + 8);
		doc.text(titleLines, left, y);
		y += titleLines.length * 24 + 8;

		if (normalized.tags.length) {
			writeParagraph(`Tags: ${normalized.tags.join(', ')}`, 11, 8);
		}

		writeParagraph(normalized.description, 12, 20);

		writeHeading('Zutaten');
		if (normalized.ingredients.length) {
			normalized.ingredients.forEach(ingredient => {
				const line = `- ${ingredient}`;
				writeParagraph(line, 12, 4);
			});
		} else {
			writeParagraph('Keine Zutaten vorhanden.', 12, 8);
		}

		y += 20;
		writeHeading('Zubereitung');
		if (normalized.instructions.length) {
			normalized.instructions.forEach(step => {
				writeParagraph(step, 12, 6);
			});
		} else {
			writeParagraph('Keine Zubereitungsschritte vorhanden.', 12, 8);
		}

		doc.save(`${sanitizeFileName(title)}.pdf`);
	};
})();

(function attachTagPillInteractions() {
	const userTagNames = new Set();

	function normalizeTagName(tagName) {
		return String(tagName || '').trim().toLocaleLowerCase('de');
	}

	function getCurrentUserId() {
		const dashboardRoot = document.getElementById('dashboard-content-stack');
		if (dashboardRoot && dashboardRoot.dataset.userId) {
			return dashboardRoot.dataset.userId;
		}

		const favouritesRoot = document.getElementById('favourites-page');
		if (favouritesRoot && favouritesRoot.dataset.userId) {
			return favouritesRoot.dataset.userId;
		}

		const cookieMatch = document.cookie.match(/(?:^|; )user_id=([^;]+)/);
		return cookieMatch ? decodeURIComponent(cookieMatch[1]) : null;
	}

	function refreshMyTagsSection(tags) {
		const tagList = document.getElementById('my-tags-list');
		const emptyText = document.getElementById('my-tags-empty');

		userTagNames.clear();
		(tags || []).forEach(tag => userTagNames.add(normalizeTagName(tag.name)));
		syncAllTagPillStates();

		if (!tagList || !emptyText) return;

		tagList.innerHTML = '';
		if (!Array.isArray(tags) || !tags.length) {
			emptyText.classList.remove('hidden');
			return;
		}

		emptyText.classList.add('hidden');
		tags
			.slice()
			.sort((a, b) => String(a.name || '').localeCompare(String(b.name || ''), 'de'))
			.forEach(tag => {
				const pill = document.createElement('span');
				pill.className = 'tag-pill';
				pill.textContent = tag.name;
				tagList.appendChild(pill);
			});

		syncAllTagPillStates();
	}

	async function fetchCurrentUserTags() {
		const userId = getCurrentUserId();
		if (!userId) return false;

		const response = await fetch(`/user/${userId}/tags`);
		if (!response.ok) return false;

		const payload = await response.json();
		refreshMyTagsSection(payload.tags || []);
		return true;
	}

	function syncTagPillState(tagPill) {
		if (!tagPill || tagPill.classList.contains('tag-pill-button')) return;
		const tagName = String(tagPill.textContent || '').trim();
		const hasTag = userTagNames.has(normalizeTagName(tagName));
		tagPill.classList.toggle('tag-pill-user-has-tag', hasTag);
	}

	function syncAllTagPillStates() {
		document.querySelectorAll('.tag-pill').forEach(syncTagPillState);
	}

	function syncTagPillsInNode(node) {
		if (!(node instanceof Element)) return;

		if (node.classList.contains('tag-pill')) {
			syncTagPillState(node);
		}

		node.querySelectorAll('.tag-pill').forEach(syncTagPillState);
	}

	async function addTagForCurrentUserByName(tagName) {
		const userId = getCurrentUserId();
		if (!userId || !tagName) return false;

		const response = await fetch(`/user/${userId}/tags/by-name/${encodeURIComponent(tagName)}`, {
			method: 'POST'
		});
		if (!response.ok) return false;

		const payload = await response.json();
		refreshMyTagsSection(payload.tags || []);
		return true;
	}

	async function removeTagForCurrentUserByName(tagName) {
		const userId = getCurrentUserId();
		if (!userId || !tagName) return false;

		const response = await fetch(`/user/${userId}/tags/by-name/${encodeURIComponent(tagName)}`, {
			method: 'DELETE'
		});
		if (!response.ok) return false;

		const payload = await response.json();
		refreshMyTagsSection(payload.tags || []);
		return true;
	}

	function showTagPillFeedback(tagPill, feedbackType) {
		if (!tagPill) return;
		const addClass = 'tag-pill-added-feedback';
		const removeClass = 'tag-pill-removed-feedback';
		tagPill.classList.remove(addClass, removeClass);

		if (feedbackType === 'remove') {
			tagPill.classList.add(removeClass);
		} else {
			tagPill.classList.add(addClass);
		}

		window.setTimeout(() => {
			tagPill.classList.remove(addClass, removeClass);
		}, 900);
	}

	document.addEventListener('click', async event => {
		const tagPill = event.target.closest('.tag-pill');
		if (!tagPill) return;

		if (tagPill.classList.contains('tag-pill-button')) {
			return;
		}

		const tagName = String(tagPill.textContent || '').trim();
		if (!tagName) return;

		const userId = getCurrentUserId();
		if (!userId) return;

		event.stopPropagation();
		const isAlreadyInUserTags = userTagNames.has(normalizeTagName(tagName));
		const ok = isAlreadyInUserTags
			? await removeTagForCurrentUserByName(tagName)
			: await addTagForCurrentUserByName(tagName);

		if (ok) {
			showTagPillFeedback(tagPill, isAlreadyInUserTags ? 'remove' : 'add');
		}
	});

	// Keep hover icon (+ / checkmark) correct for tag pills that are rendered after initial page load.
	document.addEventListener('mouseover', event => {
		const tagPill = event.target.closest('.tag-pill');
		if (!tagPill) return;
		syncTagPillState(tagPill);
	});

	const tagPillObserver = new MutationObserver((mutations) => {
		mutations.forEach((mutation) => {
			mutation.addedNodes.forEach(syncTagPillsInNode);
		});
	});

	tagPillObserver.observe(document.body, {
		childList: true,
		subtree: true
	});

	fetchCurrentUserTags();
})();
