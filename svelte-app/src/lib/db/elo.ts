const K_FACTOR = 32;

export function calculateElo(winnerRating: number, loserRating: number) {
	const expectedWinner = 1 / (1 + Math.pow(10, (loserRating - winnerRating) / 400));
	const expectedLoser = 1 / (1 + Math.pow(10, (winnerRating - loserRating) / 400));

	const winnerGain = Math.round(K_FACTOR * (1 - expectedWinner));
	const loserLoss = Math.round(K_FACTOR * expectedLoser);

	return {
		newWinnerRating: winnerRating + winnerGain,
		newLoserRating: loserRating - loserLoss,
		winnerGain,
		loserLoss
	};
}
