"""assets 모듈 테스트."""

from __future__ import annotations

from unittest.mock import patch

from ppt_maker.assets.converter import svg_to_png
from ppt_maker.assets.manager import AssetManager
from ppt_maker.assets.simple_icons import AUTO_BRAND_SLUGS, resolve_slug


class TestResolveSlug:
    def test_exact_match(self):
        assert resolve_slug("bmw") == "bmw"

    def test_auto_brand_slugs(self):
        assert resolve_slug("mercedes-benz") is not None
        assert resolve_slug("volkswagen") is not None

    def test_normalization(self):
        # 대소문자 무시
        slug = resolve_slug("BMW")
        assert slug == "bmw"

    def test_unknown_brand(self):
        result = resolve_slug("completely-unknown-brand-xyz-123")
        # slug 변환은 시도하되 결과는 검증하지 않음 (CDN에서 확인)
        assert isinstance(result, str) or result is None


class TestAutoBrandSlugs:
    def test_has_automotive_brands(self):
        """주요 자동차 브랜드가 매핑되어 있는지 확인."""
        automotive = ["bmw", "audi", "mercedes-benz", "volkswagen", "porsche"]
        for brand in automotive:
            assert brand in AUTO_BRAND_SLUGS, f"{brand} missing from AUTO_BRAND_SLUGS"

    def test_slug_values_are_strings(self):
        for key, value in AUTO_BRAND_SLUGS.items():
            assert isinstance(value, str), f"{key} has non-string slug"


class TestSvgToPng:
    def test_svg_to_png_output_path(self, tmp_path):
        """SVG → PNG 변환 (cairosvg 모킹)."""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text("<svg></svg>")
        png_file = tmp_path / "test.png"

        with patch("cairosvg.svg2png") as mock_svg2png:
            result = svg_to_png(svg_file, png_file, width=128)

        assert result == png_file
        mock_svg2png.assert_called_once()

    def test_svg_to_png_default_output(self, tmp_path):
        svg_file = tmp_path / "icon.svg"
        svg_file.write_text("<svg></svg>")

        with patch("cairosvg.svg2png"):
            result = svg_to_png(svg_file)

        assert result == tmp_path / "icon.png"


class TestAssetManager:
    def test_find_local_png(self, tmp_path):
        """로컬 PNG 파일 검색."""
        # 로컬 에셋 생성
        (tmp_path / "bmw.png").write_bytes(b"fake png")

        manager = AssetManager(local_dirs=[tmp_path])
        result = manager.find_brand_image("BMW")
        assert result is not None
        assert result.name == "bmw.png"

    def test_find_local_svg_converts(self, tmp_path):
        """로컬 SVG → PNG 변환."""
        (tmp_path / "audi.svg").write_text("<svg></svg>")

        with patch("ppt_maker.assets.manager.svg_to_png") as mock_convert:
            mock_convert.return_value = tmp_path / "audi.png"
            manager = AssetManager(local_dirs=[tmp_path])
            result = manager.find_brand_image("Audi")

        assert result is not None
        mock_convert.assert_called_once()

    def test_fallback_to_cdn(self, tmp_path):
        """로컬에 없으면 CDN 검색."""
        with (
            patch("ppt_maker.assets.manager.resolve_slug", return_value="bmw"),
            patch("ppt_maker.assets.manager.fetch_icon_svg") as mock_fetch,
            patch("ppt_maker.assets.manager.svg_to_png") as mock_convert,
        ):
            mock_svg = tmp_path / "bmw.svg"
            mock_svg.write_text("<svg></svg>")
            mock_fetch.return_value = mock_svg
            mock_convert.return_value = tmp_path / "bmw.png"

            manager = AssetManager(local_dirs=[])
            result = manager.find_brand_image("BMW")

        assert result is not None

    def test_not_found(self):
        """어디에도 없으면 None."""
        with (
            patch("ppt_maker.assets.manager.resolve_slug", return_value=None),
        ):
            manager = AssetManager(local_dirs=[])
            result = manager.find_brand_image("nonexistent-brand-xyz")

        assert result is None

    def test_add_local_dir(self, tmp_path):
        manager = AssetManager()
        manager.add_local_dir(tmp_path)
        assert tmp_path in manager._local_dirs

    def test_add_local_dir_nonexistent(self, tmp_path):
        manager = AssetManager()
        manager.add_local_dir(tmp_path / "nonexistent")
        assert len(manager._local_dirs) == 0
