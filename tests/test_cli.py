import io
import os
import subprocess
import sys
import unittest
from unittest import mock

from sfpl import exceptions
from sfpl.cli import main
from sfpl.sfpl import Book, List, User


class NonInteractiveInput(io.StringIO):
    def isatty(self):
        return False


def book(title="Python", author="Author", status=None):
    return Book(
        {"title": title, "subtitle": "", "author": author, "_id": "123"},
        status=status,
    )


class CLITest(unittest.TestCase):
    def invoke(self, argv, environ=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        status = main(
            argv,
            stdout=stdout,
            stderr=stderr,
            environ={} if environ is None else environ,
            input_stream=NonInteractiveInput(),
        )
        return status, stdout.getvalue(), stderr.getvalue()

    def test_module_help_lists_commands_without_network(self):
        result = subprocess.run(
            [sys.executable, "-m", "sfpl", "--help"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("commands:", result.stdout)
        self.assertNotIn("positional arguments:", result.stdout)
        self.assertNotIn("{search,advanced-search,branch-hours,account}", result.stdout)
        for command in ("search", "advanced-search", "branch-hours", "account"):
            self.assertIn(command, result.stdout)

    def test_nested_help_uses_compact_labels(self):
        cases = (
            (["search", "--help"], "--type TYPE", "{keyword,title"),
            (["advanced-search", "--help"], "--match MODE", "{all,any}"),
            (["account", "--help"], "commands:", "positional arguments:"),
        )
        for arguments, expected, unexpected in cases:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "-m", "sfpl", *arguments],
                    cwd=os.path.dirname(os.path.dirname(__file__)),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)
                self.assertNotIn(unexpected, result.stdout)

    @mock.patch("sfpl.cli.Search")
    def test_search_text_flattens_requested_pages(self, search_class):
        search_class.return_value.getResults.return_value = iter(
            [[book("First")], [book("Second", status="Due tomorrow")]]
        )

        status, stdout, stderr = self.invoke(
            ["search", "python", "--type", "title", "--pages", "2"]
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        search_class.assert_called_once_with("python", _type="title", format=None, sort=None, on_order=None)
        search_class.return_value.getResults.assert_called_once_with(pages=2)
        self.assertEqual(
            stdout,
            "First — Author\nSecond — Author (Due tomorrow)\n",
        )

    @mock.patch("sfpl.cli.Search")
    def test_search_with_format_and_sort(self, search_class):
        search_class.return_value.getResults.return_value = iter([[book("Album")]])

        status, stdout, stderr = self.invoke(
            ["search", "music", "--format", "LP", "--sort", "newly_acquired", "--on-order"]
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        search_class.assert_called_once_with(
            "music", _type="keyword", format="LP", sort="newly_acquired", on_order=True
        )
        self.assertEqual(stdout, "Album — Author\n")

    @mock.patch("sfpl.cli.Search")
    def test_search_with_no_results_succeeds(self, search_class):
        def no_results():
            return
            yield

        search_class.return_value.getResults.return_value = no_results()

        status, stdout, stderr = self.invoke(["search", "missing"])

        self.assertEqual(status, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    @mock.patch("sfpl.cli.Search")
    def test_search_keeps_results_when_pagination_ends(self, search_class):
        def one_page():
            yield [book("First")]

        search_class.return_value.getResults.return_value = one_page()

        status, stdout, stderr = self.invoke(["search", "python", "--pages", "2"])

        self.assertEqual(status, 0)
        self.assertEqual(stdout, "First — Author\n")
        self.assertEqual(stderr, "")

    @mock.patch("sfpl.cli.Search")
    def test_list_search_uses_text_output(self, search_class):
        result = List(
            {
                "type": "Topic Guide",
                "title": "San Francisco",
                "user": User("reader", "42"),
                "createdon": "July 1",
                "itemcount": 3,
                "description": "Local books",
                "id": "99",
            }
        )
        search_class.return_value.getResults.return_value = iter([[result]])

        status, stdout, _ = self.invoke(["search", "san francisco", "--type", "list"])

        self.assertEqual(status, 0)
        self.assertEqual(stdout, "San Francisco — reader (3 items)\n")

    @mock.patch("sfpl.cli.AdvancedSearch")
    def test_advanced_search_builds_distinct_filters(self, search_class):
        search_class.return_value.getResults.return_value = iter([[book()]])

        status, _, stderr = self.invoke(
            [
                "advanced-search",
                "--include",
                "author=J. K. Rowling",
                "--include",
                "keyword=magic",
                "--exclude",
                "title=Harry Potter",
                "--match",
                "any",
                "--pages",
                "2",
            ]
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        search_class.assert_called_once_with(
            exclusive=False,
            format=None,
            sort=None,
            on_order=None,
            includeauthor="J. K. Rowling",
            includekeyword="magic",
            excludetitle="Harry Potter",
        )
        search_class.return_value.getResults.assert_called_once_with(pages=2)

    @mock.patch("sfpl.cli.AdvancedSearch")
    def test_advanced_search_with_format_and_sort(self, search_class):
        search_class.return_value.getResults.return_value = iter([[book()]])

        status, _, stderr = self.invoke(
            [
                "advanced-search",
                "--include",
                "author=Miles Davis",
                "--format",
                "LP",
                "--sort",
                "newly_acquired",
            ]
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        search_class.assert_called_once_with(
            exclusive=True,
            format="LP",
            sort="newly_acquired",
            on_order=None,
            includeauthor="Miles Davis",
        )

    def test_advanced_search_rejects_duplicate_field(self):
        status, _, stderr = self.invoke(
            [
                "advanced-search",
                "--include",
                "author=Ursula K. Le Guin",
                "--include",
                "author=Octavia E. Butler",
            ]
        )
        self.assertEqual(status, 2)
        self.assertIn("duplicate include filter for field 'author'", stderr)

    def test_advanced_search_rejects_exclude_only(self):
        status, _, stderr = self.invoke(
            ["advanced-search", "--exclude", "title=Harry Potter"]
        )
        self.assertEqual(status, 2)
        self.assertIn("requires at least one --include", stderr)

    def test_advanced_search_rejects_invalid_filter(self):
        status, _, stderr = self.invoke(
            ["advanced-search", "--include", "unknown=value"]
        )
        self.assertEqual(status, 2)
        self.assertIn("expected FIELD=TERM", stderr)
        self.assertNotIn("Traceback", stderr)

    @mock.patch("sfpl.cli.Branch")
    def test_branch_hours_supports_unquoted_names(self, branch_class):
        branch_class.return_value.name = "west portal"
        branch_class.return_value.getHours.return_value = {
            "Sun": "1 - 5",
            "Mon": "10 - 6",
        }

        status, stdout, stderr = self.invoke(["branch-hours", "west", "portal"])

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        branch_class.assert_called_once_with("west portal")
        self.assertEqual(stdout, "west portal\nSun: 1 - 5\nMon: 10 - 6\n")

    @mock.patch("sfpl.cli.Account")
    def test_account_holds_uses_environment_credentials(self, account_class):
        account_class.return_value.getHolds.return_value = [
            book("Reserved", status="READY")
        ]

        status, stdout, stderr = self.invoke(
            ["account", "holds"],
            {"SFPL_BARCODE": "card", "SFPL_PIN": "secret"},
        )

        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        account_class.assert_called_once_with("card", "secret")
        self.assertEqual(stdout, "Reserved — Author (READY)\n")
        self.assertNotIn("secret", stdout)

    @mock.patch("sfpl.cli.Account")
    def test_account_checkouts_accepts_barcode_option(self, account_class):
        account_class.return_value.getCheckouts.return_value = [book("Borrowed")]

        status, stdout, _ = self.invoke(
            ["account", "checkouts", "--barcode", "card"], {"SFPL_PIN": "1234"}
        )

        self.assertEqual(status, 0)
        account_class.assert_called_once_with("card", "1234")
        self.assertIn("Borrowed", stdout)

    def test_noninteractive_account_requires_pin_without_echoing_credentials(self):
        status, _, stderr = self.invoke(["account", "holds", "--barcode", "card"], {})
        self.assertEqual(status, 2)
        self.assertIn("PIN is required", stderr)
        self.assertNotIn("card", stderr)

    @mock.patch("sfpl.cli.Branch", side_effect=exceptions.NoBranchFound("missing"))
    def test_domain_errors_are_concise(self, _branch_class):
        status, _, stderr = self.invoke(["branch-hours", "missing"])
        self.assertEqual(status, 1)
        self.assertEqual(stderr, "sfpl: error: No matches found for missing.\n")
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
