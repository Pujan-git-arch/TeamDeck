import apiClient from "./apiClient";

import type { LoginCredentials, TokenResponse } from "../types/auth";

export const login = async (
    credentials: LoginCredentials,
): Promise<TokenResponse> => {
    const formData = new URLSearchParams();

    formData.append("username", credentials.email);
    formData.append("password", credentials.password);

    const response = await apiClient.post <TokenResponse>(
        "/auth/login",
        formData,
        {
            headers:{
                "Content-Type": "application/x-www-form-urlencoded",
            },
        },
    );
    return response.data;
};

