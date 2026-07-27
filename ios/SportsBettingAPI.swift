import Foundation

struct PredictionRequest: Codable {
    let sport: String
    let homeTeam: String
    let awayTeam: String
    let vegasSpread: Double
    let features: [String: Double]

    enum CodingKeys: String, CodingKey {
        case sport
        case homeTeam = "home_team"
        case awayTeam = "away_team"
        case vegasSpread = "vegas_spread"
        case features
    }
}

struct EdgeResult: Codable {
    let discrepancy: Double
    let threshold: Double
    let recommendation: String
    let confidence: Double
}

struct PredictionResponse: Codable {
    let sport: String
    let homeTeam: String?
    let awayTeam: String?
    let vegasSpread: Double
    let predictedSpread: Double
    let probHomeCover: Double
    let edge: EdgeResult

    enum CodingKeys: String, CodingKey {
        case sport
        case homeTeam = "home_team"
        case awayTeam = "away_team"
        case vegasSpread = "vegas_spread"
        case predictedSpread = "predicted_spread"
        case probHomeCover = "prob_home_cover"
        case edge
    }
}

final class SportsBettingAPI {
    private let baseURL: URL

    init(baseURL: URL) {
        self.baseURL = baseURL
    }

    func predict(request: PredictionRequest) async throws -> PredictionResponse {
        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("predict"))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        guard let httpResponse = response as? HTTPURLResponse,
              (200..<300).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(PredictionResponse.self, from: data)
    }
}

// Example usage:
// let api = SportsBettingAPI(baseURL: URL(string: "https://<FUNCTION_APP>.azurewebsites.net")!)
// let request = PredictionRequest(sport: "NFL", homeTeam: "KC", awayTeam: "BUF", vegasSpread: -2.5,
//                                 features: ["home_win_pct": 0.72, "away_win_pct": 0.65, "home_rest_days": 7, "away_rest_days": 6, "home_injuries": 1, "away_injuries": 2, "recent_form_delta": 0.15])
// let response = try await api.predict(request: request)
