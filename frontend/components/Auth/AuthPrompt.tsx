import React, { useState } from "react";
import { Grid, Button } from "semantic-ui-react";
import AboutModal from "../LandingPage/AboutModal";
import { useRouter } from "next/router";
import styles from "../../styles/landingpage.module.css";
import { NextRouter } from "next/router";


const AuthPrompt = (): JSX.Element => {
    const [showAboutModal, setShowAboutModal] = useState(false);
    const router: NextRouter = useRouter();
    return (
        <div
            style={{
                height: "100%",
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}
        >
            <Grid columns={1} textAlign="center">
                <Grid.Row only="computer tablet">
                    <img
                        src="ohq-login.png"
                        width="600px"
                        height="107px"
                        alt="logo"
                    />
                </Grid.Row>
                <Grid.Row only="mobile">
                    <img
                        src="ohq.png"
                        width="217px"
                        height="107px"
                        alt="logo-mini"
                    />
                </Grid.Row>
                <Grid.Row>
                    <Button
                        style={{ width: "340px" }}
                        href={`/api/accounts/login/?next=${router.pathname}`}
                    >
                        Log In
                </Button>
                </Grid.Row>
                <div
                    className={`${styles.about} ${styles["about-landing"]}`}
                    onClick={() => setShowAboutModal(true)}
                >
                    <label>About</label>
                </div>
                <AboutModal
                    open={showAboutModal}
                    closeFunc={() => setShowAboutModal(false)}
                />
            </Grid>
        </div>
    )
}
export default AuthPrompt