import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bot import get_team, check_unlocks, data, bot, complete, leaderboard, team, boards

def generate_board(size):
    board = {}
    for row in range(size):
        row_letter = chr(ord('A') + row)
        for col in range(1, size + 1):
            key = f"{row_letter}{col}"
            board[key] = {"complete": False, "name": "Test", "details": "Test"}
    return board

class SkillIssueTests(unittest.TestCase):

    def setUp(self):
        global data
        full_board = generate_board(3)

        data.clear()
        data.update({
            "teams": {
                "Team 1": {
                    "members": ["111"],
                    "points": 19,
                    "unlocked_tiers": ["easy", "medium"],
                    "boards": {
                        "easy": full_board.copy(),
                        "medium": full_board.copy(),
                        "hard": full_board.copy()
                    }
                },
                "Team 2": {
                    "members": ["222"],
                    "points": 5,
                    "unlocked_tiers": ["easy"],
                    "boards": {
                        "easy": full_board.copy()
                    }
                }
            },
            "tier_thresholds": {"easy": 0, "medium": 0, "hard": 20, "elite": 40, "master": 65, "gm": 100},
            "tile_points": {"easy": 1, "medium": 2, "hard": 3, "elite": 4, "master": 5, "gm": 6}
        })

    def test_get_team(self):
        self.assertEqual(get_team("111"), "Team 1")
        self.assertEqual(get_team("222"), "Team 2")
        self.assertIsNone(get_team("999"))

    def test_check_unlocks(self):
        data["teams"]["Team 1"]["points"] = 21
        check_unlocks("Team 1")
        self.assertIn("hard", data["teams"]["Team 1"]["unlocked_tiers"])

    def test_complete_tile_logic(self):
        team = data["teams"]["Team 1"]
        self.assertFalse(team["boards"]["easy"]["A1"]["complete"])
        team["boards"]["easy"]["A1"]["complete"] = True
        team["points"] += data["tile_points"]["easy"]
        self.assertTrue(team["boards"]["easy"]["A1"]["complete"])
        self.assertEqual(team["points"], 20)

    @patch("skill_issue_bot.save_data")
    def test_complete_command(self, mock_save):
        mock_ctx = MagicMock()
        mock_ctx.author.id = "111"
        mock_ctx.send = AsyncMock()
        asyncio.run(complete.callback(mock_ctx, "easy", "A1"))

        self.assertTrue(data["teams"]["Team 1"]["boards"]["easy"]["A1"]["complete"])
        self.assertEqual(data["teams"]["Team 1"]["points"], 20)
        mock_ctx.send.assert_called()
        mock_save.assert_called()

    @patch("skill_issue_bot.save_data")
    def test_complete_command_case_insensitive(self, mock_save):
        mock_ctx = MagicMock()
        mock_ctx.author.id = "111"
        mock_ctx.send = AsyncMock()
        asyncio.run(complete.callback(mock_ctx, "easy", "a1"))

        self.assertTrue(data["teams"]["Team 1"]["boards"]["easy"]["A1"]["complete"])
        mock_ctx.send.assert_called()
        mock_save.assert_called()

    def test_leaderboard_command(self):
        mock_ctx = MagicMock()
        mock_ctx.send = AsyncMock()
        asyncio.run(leaderboard.callback(mock_ctx))
        mock_ctx.send.assert_called()

    def test_team_command(self):
        mock_ctx = MagicMock()
        mock_ctx.author.id = "111"
        mock_ctx.send = AsyncMock()
        asyncio.run(team.callback(mock_ctx))
        mock_ctx.send.assert_called()

    def test_boards_command(self):
        mock_ctx = MagicMock()
        mock_ctx.author.id = "111"
        mock_ctx.send = AsyncMock()
        asyncio.run(boards.callback(mock_ctx))
        mock_ctx.send.assert_called()

    @patch("skill_issue_bot.save_data")
    def test_complete_triggers_unlock(self, mock_save):
        mock_ctx = MagicMock()
        mock_ctx.author.id = "111"
        mock_ctx.send = AsyncMock()

        # Manually set points to one below hard unlock threshold
        data["teams"]["Team 1"]["points"] = 19

        # Complete a tile worth 1 point to hit 20
        asyncio.run(complete.callback(mock_ctx, "easy", "A1"))

        self.assertIn("hard", data["teams"]["Team 1"]["unlocked_tiers"])
        mock_ctx.send.assert_called()

if __name__ == "__main__":
    unittest.main()
