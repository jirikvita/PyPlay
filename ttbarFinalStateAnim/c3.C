{
//=========Macro generated from canvas: c3/c3
//=========  (Tue Feb 17 12:04:22 2015) by ROOT version5.34/14
   TCanvas *c3 = new TCanvas("c3", "c3",605,219,790,777);
   c3->Range(0,0,1,1);
   c3->SetFillColor(0);
   c3->SetBorderMode(0);
   c3->SetBorderSize(2);
   c3->SetFrameBorderMode(0);
   TLine *line = new TLine(0.4743758,0.5150555,0.5547074,0.6431425);
   line->SetLineColor(2);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.4730618,0.5108538,0.4296978,0.3645008);
   line->SetLineColor(4);
   line->SetLineWidth(3);
   line->Draw();
   TCurlyLine *curlyline = new TCurlyLine(0.5547074,0.644474,0.7048346,0.7390146,0.02,0.01);
   curlyline->SetWavy();

   Int_t ci;   // for color index setting
   ci = TColor::GetColor("#009900");
   curlyline->SetLineColor(ci);
   curlyline->SetLineWidth(3);
   curlyline->Draw();
   curlyline = new TCurlyLine(0.4283837,0.362916,0.2982917,0.2662441,0.02,0.01);
   curlyline->SetWavy();

   ci = TColor::GetColor("#009900");
   curlyline->SetLineColor(ci);
   curlyline->SetLineWidth(3);
   curlyline->Draw();
   line = new TLine(0.4270696,0.3597464,0.4454665,0.1917591);
   line->SetLineColor(6);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.5559796,0.6404794,0.5152672,0.8189081);
   line->SetLineColor(6);
   line->SetLineWidth(3);
   line->Draw();
   TLatex *   tex = new TLatex(0.5394402,0.5472703,"t");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4178712,0.429477,"#bar{t}");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4885496,0.6990679,"b");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4599212,0.2586989,"#bar{b}");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.653944,0.644474,"W");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.3127464,0.3373676,"W");
   tex->SetLineWidth(2);
   tex->Draw();
   line = new TLine(0.7048346,0.7363515,0.8587786,0.7110519);

   ci = TColor::GetColor("#ff6600");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.7022901,0.7376831,0.7582697,0.8721704);

   ci = TColor::GetColor("#ff6600");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.2969777,0.2648336,0.2667543,0.09985528);

   ci = TColor::GetColor("#0099ff");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.2969777,0.2633864,0.1498029,0.2199711);

   ci = TColor::GetColor("#0099ff");
   line->SetLineColor(ci);
   line->SetLineWidth(3);
   line->Draw();

   tex = new TLatex(0.7366412,0.8868176,"l");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.8753181,0.6551265,"#nu");
   tex->SetTextAngle(356.6335);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.2116041,0.07905687,"q'");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.1006826,0.1983356,"#bar{q}");
   tex->SetLineWidth(2);
   tex->Draw();
   line = new TLine(0.4185751,0.5765646,0.4720102,0.5099867);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(0.3931298,0.563249,0.4669211,0.5126498);
   line->SetLineWidth(2);
   line->Draw();
   line = new TLine(0.3918575,0.5286285,0.4669211,0.5113182);
   line->SetLineWidth(2);
   line->Draw();

   TMarker *marker = new TMarker(0.4743758,0.5094067,29);
   ci = TColor::GetColor("#ffcc00");
   marker->SetMarkerColor(ci);
   marker->SetMarkerStyle(29);
   marker->SetMarkerSize(3);
   marker->Draw();


   c3->Modified();
   c3->cd();
   c3->SetSelected(c3);
   c3->ToggleToolBar();

   c3->Print("c3.png");
   c3->Print("c3.pdf");
}
