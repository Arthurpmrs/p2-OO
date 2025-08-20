import os
from cms.models import MediaBlock, Post, TextBlock, Language


def display_seo_report(post: Post, language: Language):
    content = post.get_content_by_language(language)
    title = content.title
    blocks = content.body

    word_count = 0
    alt_texts: list[str] = []
    text_blocks: list[str] = []
    keywords: dict[str, int] = {}

    for block in blocks:
        if isinstance(block, TextBlock):
            text_blocks.append(block.text)
            words = block.text.lower().split()
            word_count += len(words)
            for word in words:
                if len(word) > 3:
                    keywords[word] = keywords.get(word, 0) + 1

        elif isinstance(block, MediaBlock):
            alt_texts.append(block.alt)

    title_length = len(title)
    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    repeated_words = [k for k, v in keywords.items() if v > 5]

    os.system("clear")
    print("Análise SEO do Post\n")
    print(f"Título: {title}")
    print(f"- Tamanho do título: {title_length} caracteres")
    if title_length > 60:
        print("[!] O título está muito longo (ideal < 60).")

    print(f"- Número total de palavras: {word_count}")
    if word_count < 300:
        print("[!] O texto tem poucas palavras (ideal > 300).")

    print("- Principais palavras-chave:")
    for word, count in top_keywords:
        print(f"  - {word} ({count}x)")

    if repeated_words:
        print("[!] Palavras muito repetidas:")
        print(", ".join(repeated_words))

    if not alt_texts or any(alt.strip() == "" for alt in alt_texts):
        print("[!] Algumas imagens estão sem texto alternativo (alt).")

    print("\nAnálise finalizada.", end=" ")
