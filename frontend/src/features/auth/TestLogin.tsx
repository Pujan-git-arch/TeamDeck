import { useState } from "react";
import { login } from "../../services/authService";

const TestLogin = () => {
    const [result, setResult] =  useState("");

    const handleLogin = async () => {
        try{
            const response = await login({
                email:"superadmin@teamdeck.internal",
                password: "SuperSecret123!"
            });

            console.log(response);
            setResult(response.access_token);
        } catch (error){
            console.error(error);
            setResult("Login failed");
        }
    };

    return(
        <div>
            <button onClick={handleLogin}>Test Login</button>

            <p>{result}</p>
        </div>
    );
};

export default TestLogin;