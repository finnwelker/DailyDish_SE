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
